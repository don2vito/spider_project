import requests
import time
import json
from pandas import DataFrame
import pprint

headers={
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        'Content-Length':'6',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie':'UM_distinctid=1665688ec9c2fc-021dfe3e04501f-333b5602-232800-1665688ec9d2b; JSESSIONID=DAE10C7D612F4CD482AA84B82A51FD8A; BIGipServerpool_web_8080=!mXJADvKzhrvpVYQVWFlHXx5P/V6x14uVSFmlpBli2+dZQ0BBJUr9PsnRFlsGYdix62nnHAAT3DZY; CNZZDATA1260731735=1571296337-1539045174-https%253A%252F%252Fwww.baidu.com%252F%7C1546057226; Hm_lvt_905123a113c36971dd79389429636f4c=1545614676,1545723505,1545987969,1546058917; Hm_lpvt_905123a113c36971dd79389429636f4c=1546058919',
        'Host':'www.cnrmall.com',
        'Origin':'https://www.cnrmall.com',
        'Referer':'https://www.cnrmall.com/tv',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
        }
url='https://www.cnrmall.com/tv/get_products.json'

datas=[]

year =  int(input('输入年份：'))         
month = int(input('输入月份：'))
date0 = int(input('输入当前日期：'))
date1 = int(input('输入起始日期：'))
date2 = int(input('输入结束日期：'))

if month < 10:
    month = '0' + str(month)
for date in range(date1 - date0, date2 - date0 + 1):
    date3 = date2+date
    if date3 < 10:
        date3 = '0' + str(date3)
    day = str(year) + '/' + str(month) + '/' + str(date3)
    
    data_form={
               'code':str(date)
              }
    res = requests.post(url,data_form,headers=headers)
    json_data=json.loads(res.text)
    #pprint.pprint(json_data)
    results=json_data['data']
    for data in results:
        bdate = data['bd_btime'].split(' ')[1].split('.')[0],
        edate = data['bd_etime'].split(' ')[1].split('.')[0],
        sitem_code = str(data['sitem_code']),
        item_name = str(data['item_name']),
        sale_price = str(int(data['sale_price'])),
        try:
            link = 'https://www.cnrmall.com/goods/' + str(data['commonId'])
        except:
            pass
        print(day,''.join(list(bdate)),''.join(list(edate)),''.join(list(sitem_code)),''.join(list(item_name)),''.join(list(sale_price)),link)
        info = [day,''.join(list(bdate)),''.join(list(edate)),''.join(list(sitem_code)),''.join(list(item_name)),''.join(list(sale_price)),link]
        datas.append(info)

    time.sleep(2)
        
df=DataFrame(datas,columns=['day','bdate','edate','sitem_code','item_name','sale_price','link'])
df.to_excel('./cnrmall.xlsx',sheet_name='cnrmall',index=False,columns=['day','bdate','edate','sitem_code','item_name','sale_price','link'],encoding='utf-8')

    