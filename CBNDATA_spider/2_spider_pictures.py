# coding=gbk

import requests
import time
from lxml import etree
import os
from pandas import DataFrame
import pandas as pd
import json
import pprint
import re

def get_pics(url):
    df_pic_urls = []
    res = requests.get(url, headers=headers)
    res.encoding = 'gbk'
    selector = etree.HTML(res.text)
    result = etree.tostring(selector,encoding='utf-8')
    result_str = result.decode()
    # print(result_str)
    # pic_url_json = result_str.strip('window.__INITIAL_STATE__= ').strip(';')
    pic_url_str = re.findall('window.__INITIAL_STATE__=(.*?);</script><div class="cbn-app">',result_str,re.S)
    pic_url_json = ''.join(pic_url_str)
    # print(pic_url_json)
    pic_url_list = json.loads(pic_url_json,strict=False)
    # pprint.pprint(pic_url_list)
    try:
        pic_urls = pic_url_list['report']['watermark_image_urls']
    except TypeError:
        pass

    try:
        for pic_url in pic_urls:
            pic_url = pic_url.replace('amp;','')
            df_pic_urls.append(pic_url)
            # print(pic_url)
        # print(len(df_pic_urls))
        # print(df_pic_urls)
    except UnboundLocalError:
        pass

    return df_pic_urls

if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('precision', 3)

    temp_df = []

    t1 = time.time()

    output_path = './data_pictures'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    headers = {
              'Connection': 'keep-alive',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
              # 'Accept-Encoding': 'gzip, deflate, br',
              # 'Host': 'cfpdf.dtcj.com',
              # 'If-None-Match': "Fj574XLQAfRmAh2pK-7zzsGhGfGe",
              # 'Upgrade-Insecure-Requests': '1',
              # 'Sec-Fetch-User':'?1'
              }

    data_list = pd.read_csv('./data_tables/catalogue_urls.csv',sep=',',encoding='utf-8',engine='python')
    fake_urls_list = list(data_list['url'])
    titles_list = list(data_list['title'])

    temp_data = pd.read_csv('./data_tables/spidered_urls.csv', sep=',', encoding='utf-8', engine='python')
    temp_titles_list = list(temp_data['title'])
    temp_urls_list = list(temp_data['url'])

    fake_urls_set = set(fake_urls_list)
    titles_set = set(titles_list)
    temp_titles_set = set(temp_titles_list)
    temp_urls_set = set(temp_urls_list)

    true_titles_set = titles_set - temp_titles_set
    true_urls_set = fake_urls_set - temp_urls_set

    ture_titles_list = list(true_titles_set)
    true_urls_list = list(true_urls_set)


    for title,fake_url in zip(ture_titles_list,true_urls_list):
        if not os.path.exists(os.path.join(output_path, title)):
            os.makedirs(os.path.join(output_path, title))

        data = {
            'title': title,
            'url': fake_url
        }

        url = fake_url + '1'
        pic_urls = get_pics(url)
        for pic_url in pic_urls:
            pic_data = requests.get(pic_url, headers=headers)
            pic_name = pic_url.strip().split('?')[0].split('-')[-1].split('_')[0]
            if len(pic_name) == 1:
                pic_name = '00' + pic_name + '.jpg'
            elif len(pic_name) == 2:
                pic_name = '0' + pic_name + '.jpg'
            else:
                pic_name = pic_name + '.jpg'
            try:
                fp = open(os.path.join(output_path, title, pic_name),'wb')
            except FileNotFoundError:
                pic_name = pic_url.strip().split('?')[0].split('-')[-1].split('_')[0].split('/')[-1]
                if len(pic_name) == 1:
                    pic_name = '00' + pic_name + '.jpg'
                elif len(pic_name) == 2:
                    pic_name = '0' + pic_name + '.jpg'
                else:
                    pic_name = pic_name + '.jpg'
                fp = open(os.path.join(output_path, title, pic_name), 'wb')
            except OSError:
                pic_name = pic_url.strip().split('?')[0].split('-')[-1].split('_')[0].split('/')[-1]
                if len(pic_name) == 1:
                    pic_name = '00' + pic_name + '.jpg'
                elif len(pic_name) == 2:
                    pic_name = '0' + pic_name + '.jpg'
                else:
                    pic_name = pic_name + '.jpg'
                fp = open(os.path.join(output_path, title, pic_name), 'wb')
            fp.write(pic_data.content)
            fp.close()
            print('{} 的第 {} 张图片 下载完成！！'.format(title,pic_name.split('.')[0]))

        temp_data = temp_data.append(data,ignore_index=True)
        temp_data.to_csv(os.path.join('./data_tables', 'spidered_urls.csv'), sep=',', header=True, index=False, encoding='utf-8',columns=['title','url'])
        print('追加《{}》数据完成！！'.format(title))

    created_pdfs_df = pd.DataFrame(columns=['title'])
    created_pdfs_df.to_csv(os.path.join('./data_tables', 'created_pdfs.csv'), sep=',', header=True, index=False,encoding='utf-8', columns=['title'])
    print('《已生成 PDF 文件表》生成完成！！')

    t2 = time.time()

    print('运行共耗时： {:.1f}秒'.format(t2 - t1))