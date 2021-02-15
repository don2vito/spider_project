import requests
import pandas as pd
import time
from lxml import etree
import re
import json
import pprint
from pandas import DataFrame
import os

pd.set_option('display.max_columns',100)

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0',
           'Connection':'keep-alive',
           'Cookie':'acw_tc=76b20f4515634955620931605e75a771fb0c3cff2ee34720f38c98328b99d3; sid=4hd5TDgFOF9hDjMmJ4mPCPDuhZju4gRrd; uid=4hd5TDgFOF9hDjMmJ4mPCPDuhZju4gRrd; UM_distinctid=16c659a54d50-0f7a7aa7906183-454c092b-232800-16c659a54d6151; config.bpic=https%3A%2F%2Fimage.hao24.com%2Fimages_site%2Fweb%2FwebBanner%2F2019%2F08%2F1565166790414_1196x432.jpg; config.spic=https%3A%2F%2Fimage.hao24.com%2Fimages_site%2Fweb%2FwebBanner%2F2019%2F08%2F1565163949671_1201x48.jpg; auth=false; cleanpro=true; areaCd=03; ip=112.64.144.46; os=chrome; pm=Others; _province=%E4%B8%8A%E6%B5%B7%E5%B8%82; _city=%E4%B8%8A%E6%B5%B7%E5%B8%82; JSESSIONID=D3D3577A13FE05EBE479ABCAC9EA1380; CNZZDATA1254164787=1727201212-1565068921-https%253A%252F%252Fwww.so.com%252F%7C1565589995; cgh=1749449%2C1753374%2C%2C1745816%2C1751501%2C1745956%2C1750388%2C1755099%2C1755083%2C1755082%2C1755081%2C1754769%2C1755048%2C1755044; OZ_SI_1648=sTime=1565570063&sIndex=116; OZ_1U_1648=vid=vd491d4564878d.0&ctime=1565591627&ltime=1565591555; OZ_1Y_1648=erefer=-&eurl=https%3A//www.hao24.com/&etime=1565570063&ctime=1565591627&ltime=1565591555&compid=1648',
           'Host':'www.hao24.com'
           }

datas = []
datas2 = []
datas3 = []

def spider_one_level(url):
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    selector = etree.HTML(res.text)
    # result = etree.tostring(selector)
    # print(result)
    one_levels = selector.xpath('/html/body/div[4]/div[2]/ul/div/li/a/text()')
    one_level_urls = selector.xpath('/html/body/div[4]/div[2]/ul/div/li/a/@href')
    second_levels = selector.xpath('//*[@id="hide_mask"]/li/h2/a/text()')
    second_level_urls = selector.xpath('//*[@id="hide_mask"]/li/h2/a/@href')
    third_levels = selector.xpath('//*[@id="hide_mask"]/li/div/a/text()')
    third_level_urls = selector.xpath('//*[@id="hide_mask"]/li/div/a/@href')

    third_levels_df = []

    for third_level in third_levels:
        third_level = third_level.strip()
        third_levels_df.append(third_level)
    for i in third_levels_df:
        if i == '':
            third_levels_df.remove(i)
    # print(third_levels_df)

    for third_level,third_level_url in zip(third_levels_df,third_level_urls):
        data={
                # 'one_level':one_level.strip(),
                # 'one_level_id':one_level_url.strip().split('-')[-1].split('.')[0],
                # 'second_level':second_level.strip(),
                # 'second_level_id':second_level_url.strip().split('-')[-1].split('.')[0],
                'third_level': third_level.strip(),
                'third_level_id': third_level_url.strip().split('-')[-1].split('.')[0],
                'third_level_url':third_level_url.strip()
                }
        datas.append(data)
    df1 = DataFrame(datas)
    # print(df1)
    return df1

def spider_items_urls(url):
    urls = [url + 'p{}'.format(str(i)) for i in range(1,31)]
    for url in urls:
        url = url + '.html'
        # print(url)
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        selector = etree.HTML(res.text)
        # result = etree.tostring(selector)
        # print(result)
        pic_urls = selector.xpath('/html/body/div[4]/div[6]/div[2]/div/div[2]/div/ul/li/div[1]/a/img/@data-url')
        prices = selector.xpath('/html/body/div[4]/div[6]/div[2]/div/div[2]/div/ul/li/div[2]/text()')
        item_names = selector.xpath('/html/body/div[4]/div[6]/div[2]/div/div[2]/div/ul/li/div[3]/a/text()')
        item_urls = selector.xpath('/html/body/div[4]/div[6]/div[2]/div/div[2]/div/ul/li/div[3]/a/@href')
        # print(pic_urls)
        try:
            for pic_url,price,item_name,item_url in zip(pic_urls,prices,item_names,item_urls):
                data2 = {
                    'cat_url':url,
                    'cat_code':url.split('-')[2].split('-')[0],
                    'pic_url':pic_url.strip(),
                    'price':price.strip(),
                    'item_name':item_name.strip(),
                    'item_url':item_url.strip(),
                    'item_code':item_url.split('/')[-1].split('.')[0]
                }
                print(item_name.strip(),item_url.split('/')[-1].split('.')[0],price.strip(),item_url.strip(),pic_url.strip(),url.split('-')[2].split('-')[0])
                datas2.append(data2)
            # print(datas2)
        except requests.exceptions.ConnectionError:
            time.sleep(200)
            continue
        except TimeoutError:
            time.sleep(200)
            continue

def get_items_url(url):
    datas2 = []
    urls = [url + 'p{}'.format(str(i)) for i in range(1, 31)]
    for url in urls:
        url = url + '.html'
        # print(url)
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        selector = etree.HTML(res.text)
        # result = etree.tostring(selector)
        # print(result)
        pic_urls = selector.xpath('/html/body/div[4]/div[6]/div[2]/div/div[2]/div/ul/li/div[1]/a/img/@data-url')
        prices = selector.xpath('/html/body/div[4]/div[6]/div[2]/div/div[2]/div/ul/li/div[2]/text()')
        item_names = selector.xpath('/html/body/div[4]/div[6]/div[2]/div/div[2]/div/ul/li/div[3]/a/text()')
        item_urls = selector.xpath('/html/body/div[4]/div[6]/div[2]/div/div[2]/div/ul/li/div[3]/a/@href')
        # print(pic_urls)
        try:
            for pic_url, price, item_name, item_url in zip(pic_urls, prices, item_names, item_urls):
                data2 = {
                    'cat_url': url,
                    'cat_code': url.split('-')[2].split('-')[0],
                    'pic_url': pic_url.strip(),
                    'price': price.strip(),
                    'item_name': item_name.strip(),
                    'item_url': item_url.strip(),
                    'item_code': item_url.split('/')[-1].split('.')[0]
                }
                print(item_name.strip(), item_url.split('/')[-1].split('.')[0], price.strip(), item_url.strip(),pic_url.strip(), url.split('-')[2].split('-')[0])
                datas2.append(data2)
            # print(datas2)
            for item_url in item_urls:
                item_url = 'https://www.hao24.com/goods/comm-99-' + item_url.split('/')[-1].split('.')[0]
                get_comm_info(item_url)
        except requests.exceptions.ConnectionError:
            time.sleep(200)
            continue
        except TimeoutError:
            time.sleep(200)
            continue

def get_comm_info(url):
    urls = [url + '20-p{}'.format(str(i)) for i in range(1, 21)]
    for url in urls:
        url = url + '.do'
        print(url)
        time.sleep(2)
        try:
            res = requests.get(url, headers=headers)
            # res.encoding = 'utf-8'
            json_data = json.loads(res.text)
            # pprint.pprint(json_data)
            results = json_data['data']['commList']
            for commLists in results:
                data = {
                    'attrVals': commLists['attrVals'],
                    'commContent': commLists['commContent'],
                    'commGrade': commLists['commGrade'],
                    'commScore': commLists['commScore'],
                    'commTime': commLists['commTime'],
                    'custNm': commLists['custNm'],
                    'shopNm': commLists['shopNm'],
                    'imgUrlList': commLists['imgUrlList'],
                    'replyContent': commLists['replyContent'],
                    'item_url': 'https://www.hao24.com/goods/' + url.split('-')[-2][0:-2] + '.html',
                    'item_code': url.split('-')[-2][0:-2]
                }
                # print(data)
                print(commLists['attrVals'], commLists['commContent'], commLists['commGrade'], commLists['commScore'],commLists['commTime'], commLists['custNm'], commLists['shopNm'], commLists['imgUrlList'],commLists['replyContent'], url.split('-')[-2][0:-2])
                datas3.append(data)
            time.sleep(2)

        except requests.exceptions.MissingSchema:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(200)
            continue
        except TimeoutError:
            time.sleep(200)
            continue
        except requests.exceptions.MissingSchema:
            continue
        except TypeError:
            continue

def spider_comments(url):
    urls = [url + '20-p{}'.format(str(i)) for i in range(1, 21)]
    for url in urls:
        url = url + '.do'
        print(url)
        time.sleep(2)
        try:
            res = requests.get(url, headers=headers)
            # res.encoding = 'utf-8'
            json_data = json.loads(res.text)
            # pprint.pprint(json_data)
            results = json_data['data']['commList']
            for commLists in results:
                data = {
                        'attrVals': commLists['attrVals'],
                        'commContent': commLists['commContent'],
                        'commGrade': commLists['commGrade'],
                        'commScore': commLists['commScore'],
                        'commTime': commLists['commTime'],
                        'custNm': commLists['custNm'],
                        'shopNm': commLists['shopNm'],
                        'imgUrlList': commLists['imgUrlList'],
                        'replyContent': commLists['replyContent'],
                        'item_url':'https://www.hao24.com/goods/' + url.split('-')[-2][0:-2] + '.html',
                        'item_code':url.split('-')[-2][0:-2]
                        }
                # print(data)
                print(commLists['attrVals'],commLists['commContent'],commLists['commGrade'],commLists['commScore'],commLists['commTime'],commLists['custNm'],commLists['shopNm'],commLists['imgUrlList'],commLists['replyContent'],url.split('-')[-2][0:-2])
                datas3.append(data)
            time.sleep(2)

        except requests.exceptions.MissingSchema:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(200)
            continue
        except TimeoutError:
            time.sleep(200)
            continue
        except requests.exceptions.MissingSchema:
            continue
        except TypeError:
            continue


if __name__ == '__main__':
    '''
    # 步骤一：爬取分类表（1_1_catelog_list.xlsx）
    url = 'https://www.hao24.com/'
    df_result = spider_one_level(url)
    df_result = df_result.drop_duplicates()

    output_path = './data_list'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    df_result.to_excel(os.path.join(output_path, '1_1_catelog_list.xlsx'), sheet_name='catelog_list', index=False,columns=['third_level', 'third_level_id', 'third_level_url'], encoding='utf-8')
    # print(df_result.head())
    print('《分类表》爬取完成！！\n')
    
    # 步骤二：手工增加费雷表字段（1_2_catelog_list_after_add.xlsx）
    
    # 步骤三：爬取商品表（1_3_item_list.csv）
    output_path = './data_list'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    df_result1 = pd.read_excel(os.path.join(output_path, '1_2_catelog_list_after_add.xlsx'), sheet_name='catelog_list', header=0)
    catelogs_urls = df_result1['third_level_url']
    # catelogs_urls = ['https://www.hao24.com/goods/list-c71.html']
    for catelogs_url in catelogs_urls:
        catelogs_url = catelogs_url.split('-')[0] + '-s0-' + catelogs_url.split('-')[1].split('.')[0] + '-b0-o0-t1-a-'
        spider_items_urls(catelogs_url)
        df_result2 = DataFrame(datas2)
    # print(df_result2.head())
    df_result2 = df_result2.drop_duplicates()
    df_result2.to_csv(os.path.join(output_path, '1_3_item_list.csv'), sep=',', header=True, index=False, encoding='utf-8',columns= ['item_name','item_code','price', 'item_url','pic_url','cat_code'])
    print('《产品明细表》爬取完成！！\n')
    
    # 步骤四：合并（匹配）产品表（1_4_item_list_merged.csv）
    output_path = './data_list'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    df_result1 = pd.read_excel(os.path.join(output_path, '1_2_catelog_list_after_add.xlsx'), sheet_name='catelog_list',header=0)
    df_result2 = pd.read_csv(os.path.join(output_path, '1_3_item_list.csv'),sep=',',encoding='utf-8',engine='python')
    df_result = pd.merge(df_result2, df_result1, how='left', left_on='cat_code', right_on='third_level_id')
    df_result.to_csv(os.path.join(output_path, '1_4_item_list_merged.csv'), sep=',', header=True, index=False,encoding='utf-8', columns=['item_code', 'item_name',  'price', 'item_url', 'pic_url', 'cat_code','third_level_url','third_level','second_level','one_level'])
    print('《处理后的产品明细表》处理完成！！\n')
    '''
    # 步骤五：爬取评论表（1_5_comment_list.csv）
    output_path = './data_list'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    df_result = pd.read_excel(os.path.join(output_path, '1_2_catelog_list_after_add.xlsx'), sheet_name='catelog_list',header=0)
    items_urls = df_result['third_level_url']
    items_cates = df_result['third_level']
    for items_url,items_cate in zip(items_urls,items_cates):
        datas3 = []
        items_url = items_url.split('-')[0] + '-s0-' + items_url.split('-')[1].split('.')[0] + '-b0-o0-t1-a-'
        get_items_url(items_url)
        file_name = str(items_cate.replace('、', '_').strip())
        file_full_name = file_name + '.csv'
        df_result3 = DataFrame(datas3)
        try:
            df_result3.to_csv(os.path.join(output_path, file_full_name), sep=',', index=False, header=True,encoding='utf-8', columns=['attrVals','commContent','commGrade','commScore','commTime','custNm','shopNm','imgUrlList','replyContent','item_code'])
            print('《' + file_full_name.split('.')[0] + '  评论表》' + '爬取完成！！')
        except KeyError:
            pass

    '''
    for items_url in items_urls:
        items_url = 'https://www.hao24.com/goods/comm-99-' + items_url.split('/')[-1].split('.')[0]
        spider_comments(items_url)
        df_result3 = DataFrame(datas3)
    # df_result3 = df_result3.drop_duplicates()
    df_result3.to_csv(os.path.join(output_path, '1_5_comment_list.csv'), sep=',', header=True, index=False, encoding='utf-8',columns= ['attrVals','commContent','commGrade','commScore','commTime','custNm','shopNm','imgUrlList','replyContent','item_code'])
    print('《评论明细表》爬取完成！！\n')
    '''