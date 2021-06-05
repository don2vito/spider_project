import requests
import time
from lxml import etree
import os
from pandas import DataFrame
import pandas as pd
import random

def get_data_1st_level(url,headers):
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    selector = etree.HTML(res.text)
    # result = etree.tostring(selector)
    # print(result)

    titles = selector.xpath('//div[@id="imgbox"]/div/h2/a/text()')
    dates = selector.xpath('//div[@id="contentleft"]/div/div/div/span[2]/text()')
    level1_urls = selector.xpath('//div[@id="contentleft"]/div/div/h2/a/@href')
    # print(titles)

    for title,date,level1_url in zip(titles,dates,level1_urls):
        data = {
                'source':'IPOIPO',
                'date':date.strip(),
                'title':title.strip(),
                'category':'',
                'summary':level1_url.strip(),
                'url':level1_url.strip()
                }
        # print(date.strip(),title.strip(),level1_url.strip())
        data_table.append(data)
    # time.sleep(random.randint(3,5))

def get_file_1st_level():
    output_path = './data_tables'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    headers = {
              'Cookie': 'pgv_pvi=6858866688; cf_clearance=20f43d504f1d1e39d897a3ef25dab3b405d9657a-1614733564-0-250; UM_distinctid=178e79fb827314-037cd58bab9c9f-45410429-232800-178e79fb828207; __yjs_duid=1_5b884115319a034e882d4330e1d1a32c1619586303692; security_session_verify=823ac3a52b11213dbb4c3edf7e912a28; timezone=8; Hm_lvt_db51058e76f6bc3138825d935670f2cb=1622436050,1622599531,1622709004,1622769227; yjs_js_security_passport=8fb6df1726a0684ac4f35718b3d74d3ef177a222_1622793726_js; CNZZDATA1261284055=1599488802-1602808872-http%253A%252F%252Fipoipo.cn%252F%7C1622793511; DL_referrer=http%3A//ipoipo.cn/post/12574.html; Hm_lpvt_db51058e76f6bc3138825d935670f2cb=1622793863',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
              }

    urls = ['http://ipoipo.cn/category-6_{}.html'.format(str(i)) for i in range(17,50)]
    for url in urls:
        get_data_1st_level(url,headers)
        df = DataFrame(data_table)
        # print(df)

    df.columns = ['source','date','title','category','summary','url']
    df.to_excel(os.path.join(output_path, '3_1 IPOIPO_data_1st_level.xlsx'), header=True,index=False,sheet_name='IPOIPO_1st_level',columns=['source','date','title','category','summary','url'])
    print('《IPOIPO 一级页面信息表》爬取完成！！')
    return df

def get_data_2nd_level(url,headers):
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    selector = etree.HTML(res.text)

    tags = selector.xpath('//span[@class="padding"]/a/text()')
    level2_urls = selector.xpath('//div[@class="dlp-down"]/a/@href')
    # print(tags)

    for tag,level2_url in zip(tags,level2_urls):
        data = {
                'url':url,
                'tags':tag.strip(),
                'level2_url':level2_url.strip()
                }
        print(tag.strip(),level2_url.strip())
        df_temp.append(data)
    # time.sleep(random.randint(3,5))

if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('precision', 3)

    t1 = time.time()

    headers = {
        'Cookie': 'pgv_pvi=6858866688; cf_clearance=20f43d504f1d1e39d897a3ef25dab3b405d9657a-1614733564-0-250; UM_distinctid=178e79fb827314-037cd58bab9c9f-45410429-232800-178e79fb828207; __yjs_duid=1_5b884115319a034e882d4330e1d1a32c1619586303692; security_session_verify=823ac3a52b11213dbb4c3edf7e912a28; timezone=8; Hm_lvt_db51058e76f6bc3138825d935670f2cb=1622436050,1622599531,1622709004,1622769227; yjs_js_security_passport=8fb6df1726a0684ac4f35718b3d74d3ef177a222_1622793726_js; CNZZDATA1261284055=1599488802-1602808872-http%253A%252F%252Fipoipo.cn%252F%7C1622793511; DL_referrer=http%3A//ipoipo.cn/post/12574.html; Hm_lpvt_db51058e76f6bc3138825d935670f2cb=1622793863',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    }

    data_table = []
    df1 = get_file_1st_level()
    urls_list = list(df1['url'])
    urls_set = set(urls_list)
    df_temp = []
    for url in urls_list:
        get_data_2nd_level(url, headers)
        df2 = DataFrame(df_temp)

    output_path = './data_tables'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    df2.columns = ['url', 'tags', 'level2_url']
    df2.to_excel(os.path.join(output_path, '3_2 IPOIPO_data_2nd_level.xlsx'), header=True, index=False,sheet_name='IPOIPO_2nd_level', columns=['url', 'tags', 'level2_url'])
    print('《IPOIPO 二级页面信息表》爬取完成！！')

    df = pd.merge(df1,df2,on='url',how='left')

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d').dt.date
    df = df.rename(columns={'url': 'level1_url','level2_url': 'url'})
    # print(df)

    df.to_excel(os.path.join(output_path, '3. IPOIPO_data.xlsx'), header=True, index=False,sheet_name='IPOIPO_final', columns=['source','date','title','category','summary','tags','url'])
    print('《IPOIPO 最终信息表》爬取完成！！')

    t2 = time.time()

    print('运行共耗时 {:.1f}秒'.format(t2 - t1))