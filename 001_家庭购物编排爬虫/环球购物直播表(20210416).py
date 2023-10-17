import requests
import json
import pandas as pd
import demjson
from jsonpath import jsonpath
import time
import datetime


headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
data = pd.DataFrame()

year =  int(input('输入年份：'))
month = int(input('输入月份：'))
date1 = int(input('输入起始日期：'))
date2 = int(input('输入结束日期：'))

if month < 10:
    month = '0' + str(month)
for date in range(date1, date2 + 1):
    if date < 10:
        date = '0' + str(date)

    
    url='https://api.sharkshopping.com/ec/api?method=tv.program.data&appid=webapp&token=&version=4.4.1&source=wap&city_num=310100&brand_id=&date=' + str(year) + '-' + str(month)+ '-' + str(date) + '&cat_id='
    print(url)
    res = requests.get(url)
    json_data = demjson.decode(res.text)
    start_time_list = jsonpath(json_data, '$..start_time')
    end_time_list = jsonpath(json_data, '$..end_time')
    sku_list = jsonpath(json_data, '$..sku')
    name_list = jsonpath(json_data, '$..name')
    price_list = jsonpath(json_data, '$..price')
    product_brand_list = jsonpath(json_data, '$..product_brand')
    
    start_time_list = [i for i in start_time_list if i != 0]
    end_time_list = [i for i in end_time_list if i != 0]
    
    list_content = [start_time_list,end_time_list,sku_list,name_list,price_list,product_brand_list]
    df = pd.DataFrame(list_content)
    df = df.T
    df.rename(columns={
                        0:'开始时间（处理前）',
                        1:'结束时间（处理前）',
                        2:'商品编号',
                        3:'商品名称',
                        4:'价格',
                        5:'品牌名称',
                        },inplace=True)
    df['开始时间'] = df['开始时间（处理前）'].apply(lambda x:time.strftime("%H:%M",time.localtime(x)))
    df['结束时间'] = df['结束时间（处理前）'].apply(lambda x:time.strftime("%H:%M",time.localtime(x)))
    df['链接'] = 'https://wp.sharkshopping.com/product/' + df['商品编号']
    df['日期'] = str(year) + str(month) + str(date)
    print(df)
    data = data.append(df)
    
data.sort_values(by=['日期','开始时间'],ascending=True,inplace=True)  
data.to_excel('./ghs.xlsx',sheet_name='ghs',index=False,columns=['日期','开始时间','结束时间','商品编号','商品名称','价格','品牌名称','链接'],encoding='utf-8')
print('Excel 文件保存成功！！')