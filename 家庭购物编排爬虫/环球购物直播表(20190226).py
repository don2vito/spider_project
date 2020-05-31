import requests
import time
from lxml import etree
from pandas import DataFrame

headers={
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

    
    url='http://www.ghs.net/tvshop-shownation-' + str(date) + '.html'
    
    res=requests.get(url,headers=headers)
    res.encoding='utf-8'
    selector=etree.HTML(res.text)
    #status_code=res.status_code
    #print(status_code)
    #result = etree.tostring(selector)
    #print(result)
    
    day=str(year)+'/'+str(month)+'/'+str(date)
    date_times=selector.xpath('//tr/td[1]/strong/text()')
    ids=selector.xpath('//tr/td[3]/text()[1]')
    items=selector.xpath('//tr/td[3]/a/text()')
    prices=selector.xpath('//span[@class="tv2013red"]/script/text()')
  
    for date_time,id,item,price in zip(date_times,ids,items,prices):
        data={
              'day':day,
              'b_time':date_time.split(' - ')[0],
              'e_time':date_time.split(' - ')[1],
              'id':id.strip().split('：')[1],
              'item':item.strip(),
              'price':price.strip().split('(')[2].split('.')[0],
              'link':'https://www.ghs.net/product-' + str(id.strip().split('：')[1]) + '.html'
             }
            
        #print(data)
        print(day,date_time.split(' - ')[0],date_time.split(' - ')[1],id.strip().split('：')[1],item.strip(),price.strip().split('(')[2].split('.')[0],'https://www.ghs.net/product-' + str(id.strip().split('：')[1]) + '.html')
        datas.append(data)
        
    time.sleep(2)
  
df=DataFrame(datas)
df.to_excel('./ghs.xlsx',sheet_name='ghs',index=False,columns=['day','b_time','e_time','id','item','price','link'],encoding='utf-8')