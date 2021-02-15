import requests
import pandas as pd
import time
from lxml import etree
import re
from pandas import DataFrame
import os

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0',
           'Connection':'keep-alive'
           }

def get_items_url(url):
    data3s = []
    urls = [url + '?page.currPageNo={}'.format(str(i)) for i in range(1,31)]
    for url in urls:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        selector = etree.HTML(res.text)
        # result = etree.tostring(selector)
        # print(result)
        item_urls = selector.xpath('//div[@class="pv_shop_list_content normal_list"]/div[@class="item1 item1b item2 itemo"]/div[@class="corner_icon1"]/p/a/@href')
        pro_names = selector.xpath('//div[@class="pv_shop_list_content normal_list"]/div[@class="item1 item1b item2 itemo"]/p[@class="title"]/a/text()')
        pro_prices = selector.xpath('//div[@class="pv_shop_list_content normal_list"]/div[@class="item1 item1b item2 itemo"]/p[@class="price"]/em/text()')
        # print(item_urls)
        # print(pro_names)
        # print(pro_prices)
        for item_url,pro_name,pro_price in zip(item_urls,pro_names,pro_prices):
            data3 = {
                'cate_url':url.strip(),
                'item_url':item_url.strip(),
                'item_code':item_url.strip().split('/')[-1],
                'pro_name':pro_name.strip(),
                'pro_price':pro_price.strip().replace(',','')
            }
            # print(url.strip(),item_url.strip(),item_url.strip().split('/')[-1],pro_name.strip(),pro_price.strip().replace(',',''))
            data3s.append(data3)

        for item_url in item_urls:
            get_comm_info(str(item_url.strip().split('/')[-1]))

def get_comm_info(item_code):
    urls = ['http://www.ocj.com.cn/detail/comment/' + str(item_code) + '?page.currPageNo={}'.format(str(i)) for i in range(1, 31)]
    for url in urls:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        selector = etree.HTML(res.text)
        # result = etree.tostring(selector)
        # print(result)
        comms = selector.xpath('//div[@class="item_content"]/div[@class="content"]/text()')
        # print(comms)
        try:
            for comm in comms:
                data4 = {
                    'url':url.strip(),
                    'comment': comm.strip(),
                }
                # print(url.strip(),comm.strip())
                data4s.append(data4)
        except requests.exceptions.ConnectionError:
            time.sleep(200)
            continue
        except TimeoutError:
            time.sleep(200)
            continue
        except urllib3.exceptions.NewConnectionError:
            time.sleep(200)
            continue
        except urllib3.exceptions.MaxRetryError:
            time.sleep(200)
            continue
        except urllib3.exceptions.ProtocolError:
            time.sleep(200)
            continue

if __name__ == '__main__':
    # 步骤三：爬取评论表
    list_path = './data_list'
    if not os.path.exists(list_path):
        os.makedirs(list_path)
    df = pd.read_excel(os.path.join(list_path,'catelog_list.xlsx'), sheet_name='catelog_list', header=0)
    it_urls = df['cates_url']
    it_cates = df['cate']
    output_path = './output'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for it_url, it_cate in zip(it_urls, it_cates):
        data4s = []
        get_items_url(it_url)
        file_name = str(it_cate.replace(' ', '').replace('/', ' ').strip())
        file_full_name = file_name + '.csv'
        df_result3 = DataFrame(data4s)
        try:
            df_result3.to_csv(os.path.join(output_path, file_full_name), sep=',', index=False, header=True, encoding='utf-8',columns=['url','comment'])
            print('《' + file_full_name.split('.')[0] + '  评论表》' + '爬取完成！！')
        except KeyError:
            pass