import requests
import time
from lxml import etree
import os
from pandas import DataFrame
import pandas as pd

def get_data(url):
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    selector = etree.HTML(res.text)
    # result = etree.tostring(selector)
    # print(result)

    titles = selector.xpath('//*[@id="report-list"]/div[2]/div/div[2]/a/h4/text()')
    describes = selector.xpath('//*[@id="report-list"]/div[2]/div/div[2]/div[1]/text()')
    dates = selector.xpath('//*[@id="report-list"]/div[2]/div/div[2]/div[2]/div[1]/text()')
    # tips = selector.xpath('//*[@id="report-list"]/div[2]/div/div[2]/div[3]/div[1]/div/span/text()')
    one_level_urls = selector.xpath('//*[@id="report-list"]/div[2]/div/div[2]/a/@href')
    # print(dates)

    for title,describe,date,one_level_url in zip(titles,describes,dates,one_level_urls):
        data = {
                'title':title.strip().replace('|','_').replace(':','_').replace('？','_').replace('、','_'),
                'describe':describe.strip().replace('\n',''),
                'date':date.strip().replace('.','/'),
                # 'tip':tip.strip(),
                'url':'https://www.cbndata.com' + one_level_url.strip() +'?isReading=report&page='
                }
        print(title.strip().replace('|','_').replace(':','_').replace('？','_').replace('、','_'),describe.strip().replace('\n',''),date.strip().replace('.','/'),'https://www.cbndata.com' + one_level_url.strip() +'?isReading=report&page=')
        data_table.append(data)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('precision', 3)

    begin_page = int(input("请输入起始页（数字）："))
    end_page = int(input("请输入结束页（数字）："))

    t1 = time.time()

    output_path = './data_tables'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    headers = {
              'Content-Type': 'application/json;charset=utf-8',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
              }

    data_table = []

    urls = ['https://www.cbndata.com/report?page={}&price_category=price_free'.format(str(i)) for i in range(begin_page,end_page + 1)]
    for url in urls:
        get_data(url)
        df = DataFrame(data_table)
    df.to_csv(os.path.join(output_path, 'catalogue_urls.csv'),sep=',', header=True,index=False,encoding='utf-8',columns=['title','describe','date','url'])
    print('《CBNData 一级页面信息表》爬取完成！！')

    spidered_urls_df = pd.DataFrame(columns = ['title','url'])
    spidered_urls_df.to_csv(os.path.join(output_path, 'spidered_urls.csv'),sep=',', header=True,index=False,encoding='utf-8',columns=['title','url'])
    print('《已爬取页面链接表》生成完成！！')

    t2 = time.time()

    print('运行共耗时 {:.1f}秒'.format(t2 - t1))