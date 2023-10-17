import requests
import time
import json
from pandas import DataFrame
import pprint

headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'accept':'application/json, text/javascript, */*; q=0.01',
        # 'Connection': 'close',
        }
url = 'https://www.ugoshop.com/getTvList?channel=UGO1&date='

datas=[]

year =  int(input('输入年份：'))         
month = int(input('输入月份：'))
date1 = int(input('输入起始日期：'))
date2 = int(input('输入结束日期：'))

for date in range(date1, date2 + 1):
 
    if date < 10:
        day = '0' + str(date)
    else:
        day= str(date)
    if month < 10:
        month1 = '0' + str(month)
    else:
        month1 = str(month)
    subscribeTime = str(year) + '/' + str(month1) + '/' + str(day)
    
    time_tuple = (year,month,date,0,0,0,0,0,0)
    a=time.mktime(time_tuple)
    b=str(int(a))
    #print(b) 
    '''    
    data_form={
            'channel':'UGO1',
            'date':b
            }
    '''
    res = requests.get(url + b,headers=headers,verify=False)
    json_data=json.loads(res.text)
    #pprint.pprint(json_data)
    results=json_data['data']['tvItemList']
    for tvItemList in results:
        data={
             'subscribeTime':subscribeTime,  
             'begin':tvItemList[0]['begin'],  
             'end':tvItemList[0]['end'],  
             'goodsId':tvItemList[0]['goodsId'],
             'goodsSn':tvItemList[0]['goodsSn'],
             'goodsName':tvItemList[0]['goodsName'],
             'price':tvItemList[0]['price'],
             'link':'https://www.ugoshop.com/goods-' + str(tvItemList[0]['goodsId']) + '.html'
             }
        #print(data)
        print(subscribeTime,tvItemList[0]['begin'],tvItemList[0]['end'],tvItemList[0]['goodsId'],tvItemList[0]['goodsSn'],tvItemList[0]['goodsName'],tvItemList[0]['price'],'https://www.ugoshop.com/goods-' + str(tvItemList[0]['goodsId']) + '.html')
        datas.append(data)
        
    time.sleep(2)
    
df=DataFrame(datas)
df.to_excel('./ugoshop.xlsx',sheet_name='ugoshop',index=False,columns=['subscribeTime','begin','end','goodsId','goodsSn','goodsName','price','link'],encoding='utf-8')
