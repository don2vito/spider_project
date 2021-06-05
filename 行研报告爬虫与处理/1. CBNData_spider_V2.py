import requests
import time
from lxml import etree
import os
from pandas import DataFrame
import pandas as pd
import json

def get_data(url):
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    json_data=json.loads(res.text)
    results=json_data['data']
    for data in results:
        source = 'CBNData'
        date = data['date'].strip().split('T')[0]
        title = data['title'].strip()
        url = 'https://www.cbndata.com/report/' + str(data['id']).strip() + '/detail'
        category = data['report_category'].strip()
        summary = data['summary'].strip()
        tags = [i['name'].strip() for i in data['tags']]
        print(data['date'].strip().split('T')[0],data['title'].strip(),data['report_category'].strip(),'https://www.cbndata.com/report/' + str(data['id']).strip() + '/detail',[i['name'].strip() for i in data['tags']])
        info = ['CBNData',data['date'].strip().split('T')[0], data['title'].strip(),'https://www.cbndata.com/report/' + str(data['id']).strip() + '/detail', data['report_category'].strip(),data['summary'].strip(),[i['name'].strip() for i in data['tags']]]

        data_table.append(info)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('precision', 3)

    t1 = time.time()

    output_path = './data_tables'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    headers = {
              'Content-Type': 'application/json;charset=utf-8',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
              }

    data_table = []

    urls = ['https://www.cbndata.com/api/v2/report_products?tags[]=all&price_category=price_free&page={}&per=50'.format(str(i)) for i in range(1,4)]
    for url in urls:
        get_data(url)
        df = DataFrame(data_table)
        # print(df)

    df.columns = ['source','date','title','url','category','summary','tags']

    df['tags'] = df['tags'].apply('|'.join)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d').dt.date

    df.to_excel(os.path.join(output_path, '1. CBNData_data.xlsx'), header=True,index=False,sheet_name='CBNData',columns=['source','date','title','category','summary','tags','url'])
    print('《CBNData 一级页面信息表》爬取完成！！')

    t2 = time.time()

    print('运行共耗时 {:.1f}秒'.format(t2 - t1))