import requests
import time
import json
from pandas import DataFrame
import pprint

headers={
        'Content-Type':'application/json',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }

datas=[]

year =  int(input('输入年份：'))         
month = int(input('输入月份：'))
date1 = int(input('输入起始日期：'))
date2 = int(input('输入结束日期：'))

if month < 10:
    month = '0' + str(month)

for date in range(date1, date2 + 1):
    if date < 10:
        date = '0' + str(date)
    day = str(year) + '-' + str(month) + '-' + str(date)
    day_str = str(year) + '/' + str(month) + '/' + str(date)
    url='http://www.jyh.com/JYH/API.aspx?api_input={"date":' + '\'' + day +'\'' +',"paging":{"limit":0,"offset":0},"activity":"467703130008000100070001"}&api_target=com_cmall_familyhas_api_ApiForGetTVData'

    res = requests.get(url,headers=headers)
    res.encoding='utf-8'
    json_data=json.loads(res.text)
    products=json_data['products']
    for product in products:
        data={
              'day':day_str,
              'playTime':product['playTime'].split(' ')[1],  
              'endTime':product['endTime'].split(' ')[1],  
              'id':product['id'],
              'name':product['name'],
              'salePrice':product['salePrice'],
              'link':'http://www.jyh.com/IndexMain.html?u=ProductDetail&pid=' + str(product['id'])
              }
        #print(data)
        print(day_str,product['playTime'].split(' ')[1],product['endTime'].split(' ')[1],product['id'],product['name'],product['salePrice'],'http://www.jyh.com/IndexMain.html?u=ProductDetail&pid=' + str(product['id']))
        datas.append(data)
time.sleep(2)

df = DataFrame(datas)
df = df.sort_values(by=['day','playTime'],ascending=True)
df.to_excel('./jyh.xlsx',sheet_name='jyh',index=False,columns=['day','playTime','endTime','id','name','salePrice','link'],encoding='utf-8')
    