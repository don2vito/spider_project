import json
import requests
from pandas import DataFrame
import pprint
import time

headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.30 Safari/537.36',
        'Host':'www.happigo.com',
        'Referer':'http://www.happigo.com/tv5/'
        }

datas=[]

year =  int(input('输入年份：') )
month = int(input('输入月份：'))
date1 = int(input('输入起始日期：'))
date2 = int(input('输入结束日期：'))

if month < 10:
    month = '0' + str(month)
for date in range(date1, date2 + 1):
    if date < 10:
        date = '0' + str(date)

    day = str(year)+'/'+str(month)+'/'+str(date)
    url = 'http://www.happigo.com/shop/index.php?act=tv_live&op=ajaxTvzhiboGoods&token=ok&type=info&ymd=' + str(year) + str(month) + str(date)
    res = requests.get(url,headers=headers)
    json_data=json.loads(res.text)
    #pprint.pprint(json_data)
    results=json_data['tvliveGoods']    
    for tvliveGoods in results:
       
        data={
             'day':day,
             'tvStartTime1':tvliveGoods['tvStartTime1'],
             'tvEndTime1':tvliveGoods['tvEndTime1'],
             'goodsCommonid':tvliveGoods['goodsCommonid'],
             'tvName':tvliveGoods['tvName'],
             'salePrice':tvliveGoods['salePrice'],
             'salenum_d30':tvliveGoods['salenum_d30'],
             'link':'https://www.happigo.com/item-' + str(tvliveGoods['goodsCommonid']) + '.html'
             }
        #print(data)
        print(day,tvliveGoods['tvStartTime1'],tvliveGoods['tvEndTime1'],tvliveGoods['goodsCommonid'],tvliveGoods['tvName'],tvliveGoods['salePrice'],tvliveGoods['salenum_d30'],'https://www.happigo.com/item-' + str(tvliveGoods['goodsCommonid']) + '.html')
        datas.append(data)
    
    time.sleep(2)

df = DataFrame(datas)
df = df.drop_duplicates(subset=['tvStartTime1','tvEndTime1','goodsCommonid','tvName','salePrice','salenum_d30','link'],keep='first')
df.to_excel('./happigo.xlsx',sheet_name='happigo',index=False,columns=['day','tvStartTime1','tvEndTime1','goodsCommonid','tvName','salePrice','salenum_d30','link'],encoding='utf-8')