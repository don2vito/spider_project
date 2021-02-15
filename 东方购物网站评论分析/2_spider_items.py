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
datas2 = []

def get_items_url(url):
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
        try:
            for item_url,pro_name,pro_price in zip(item_urls,pro_names,pro_prices):
                data2 = {
                    'cates_url':url.strip().split('?')[0],
                    'cate_url':url.strip(),
                    'item_url':item_url.strip(),
                    'item_code':item_url.strip().split('/')[-1],
                    'pro_name':pro_name.strip(),
                    'pro_price':pro_price.strip().replace(',','')
                }
                # print(url.strip(),item_url.strip(),item_url.strip().split('/')[-1],pro_name.strip(),pro_price.strip().replace(',',''))
                datas2.append(data2)
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
    # 步骤二：爬取产品明细表
    output_path = './data_list'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    df_result1 = pd.read_excel(os.path.join(output_path, 'catelog_list.xlsx'),sheet_name='catelog_list',header=0)
    it_urls = df_result1['cates_url']
    for it_url in it_urls:
        get_items_url(it_url)
        df_result2 = DataFrame(datas2)
    df_result2.to_csv(os.path.join(output_path, 'items_list.csv'),sep=',', header=True,index=False,encoding='utf-8',columns=['cate_url','item_url','item_code','pro_name','pro_price'])
    print('《产品明细表》爬取完成！！\n')