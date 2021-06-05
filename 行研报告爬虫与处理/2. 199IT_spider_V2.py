import requests
import time
from lxml import etree
import os
from pandas import DataFrame
import pandas as pd
import random

def get_data(url):
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    selector = etree.HTML(res.text)
    # result = etree.tostring(selector)
    # print(result)

    titles = selector.xpath('//div[@id="content"]/article/div[2]/h2/a/text()')
    dates = selector.xpath('//div[@id="content"]/article/div[2]/aside/div/ul/li[2]/time/text()')
    tags = selector.xpath('//aside[@class="meta-row cat-row"]/div/ul/li[2]/a/text()')
    urls = selector.xpath('//div[@id="content"]/article/div[2]/h2/a/@href')
    # print(urls)

    for title,date,tag,url in zip(titles,dates,tags,urls):
        data = {
                'source':'199IT',
                'date':date.strip(),
                'title':title.strip(),
                'category':'',
                'summary':'',
                'tag':tag.strip(),
                'url':url.strip()
                }
        print(date.strip(),title.strip(),tag.strip(),url.strip())
        data_table.append(data)
    time.sleep(random.randint(5,10))

if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('precision', 3)

    t1 = time.time()

    output_path = './data_tables'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    headers = {
              'Cookie': '__utmz=155908219.1568812655.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; Hm_lvt_47366c78fc67d7eef4915d26493d8cf0=1622811688; Hm_lpvt_47366c78fc67d7eef4915d26493d8cf0=1622811688; pt_123b33d6=uid=VgbbMbukv34yCVa/hExS4g&nid=0&vid=Jq8nKT5Bm2H7XTVHmQjumQ&vn=15&pvn=1&sact=1622811688271&to_flag=0&pl=brWmBFXsDE5V4fLqiv2SaA*pt*1622811688271; pt_s_123b33d6=vt=1622811688271&cad=; __utma=155908219.1919502663.1568028144.1613548032.1622811688.13; __utmc=155908219',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
              }

    data_table = []

    urls = ['http://www.199it.com/archives/category/report/page/{}'.format(str(i)) for i in range(17,52)]
    for url in urls:
        get_data(url)
        df = DataFrame(data_table)
        # print(df)

    df['date'] = df['date'].str.replace('年','-')
    df['date'] = df['date'].str.replace('月', '-')
    df['date'] = df['date'].str.replace('日', '')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d').dt.date

    df.columns = ['source','date','title','category','summary','tags','url']
    df.to_excel(os.path.join(output_path, '2. 199IT_data.xlsx'), header=True,index=False,sheet_name='199IT',columns=['source','date','title','category','summary','tags','url'])
    print('《199IT 一级页面信息表》爬取完成！！')

    t2 = time.time()

    print('运行共耗时 {:.1f}秒'.format(t2 - t1))