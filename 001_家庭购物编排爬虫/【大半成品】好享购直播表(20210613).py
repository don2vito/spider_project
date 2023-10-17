import requests
import time
from lxml import etree
from pandas import DataFrame
import json
import re

headers={
        'Content-Type':'application/json;charset=utf-8',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
url='https://www.hao24.com/channel/live_list_body.do'

datas=[]

year =  int(input('输入年份：'))         
month = int(input('输入月份：'))
date = int(input('输入当前日期：'))

if month < 10:
    month = '0' + str(month)
    
for i in range(0,-3,-1):
    data_form={
              'areaCd':'02',
              'dsize':str(i)
              }
    json_data=json.dumps(data_form)
    res = requests.post(url,json_data,headers=headers)
    res.encoding='utf-8'
    selector=etree.HTML(res.text)

    # print(selector)
    # status_code=res.status_code
    # print(status_code)
    # result = etree.tostring(selector)
    # print(result)
    
    a=date + i
    if a < 10:
        a='0' + str(a)
    day = str(year) + '/' + str(month) + '/' + str(a)
       
    date_times = selector.xpath('//p[@class="one"]/text()')
    ids = selector.xpath('//p[@class="two"]/text()')
    titles = selector.xpath('//p[@class="title"]/a/text()')
    prices = selector.xpath('//p[@class="price"]/text()')
    links = selector.xpath('//li[@class="con second"]/a/@href')
    # print(titles)
    for date_time,id,title,price,link in zip(date_times,ids,titles,prices,links):
        data={
              'day':day,
              'b_time':date_time.strip().split('-')[0],
              'e_time':date_time.strip().split('-')[1],
              'id':id.strip().split(':')[1],
              'title':title.strip(),
              'price':price.strip().split('¥')[1].split('.')[0],
              'link':link.strip()
             }
        
        #print(data)
        print(day,date_time.strip().split('-')[0],date_time.strip().split('-')[1],id.strip().split(':')[1],title.strip(),price.strip().split('¥')[1].split('.')[0],link.strip())
        datas.append(data)
        
    time.sleep(2)
    
df=DataFrame(datas)
df.sort_values(by=['day','b_time'],ascending=[True,True],inplace=True)
df.to_excel(r'./hao24.xlsx',sheet_name='hao24',index=False,columns=['day','b_time','e_time','id','title','price','link'],encoding='utf-8')