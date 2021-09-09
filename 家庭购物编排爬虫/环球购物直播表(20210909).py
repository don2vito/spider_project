from selenium import webdriver
import time
import pandas as pd
import re
import json
import demjson
from jsonpath import jsonpath
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import requests

caps = {
    'browserName': 'chrome',
    'version': '',
    'platform': 'ANY',
    'goog:loggingPrefs': {'performance': 'ALL'},   # 记录性能日志
    'goog:chromeOptions': {'extensions': []}  # 无界面模式
}

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')

# __browser_url = r'D:\360\360se6\Application\360se.exe'  # 360浏览器的地址
# chrome_options.binary_location = __browser_url

driver=webdriver.Chrome(options=chrome_options,desired_capabilities=caps)


# 简单隐藏selenium特征
with open('./stealth.min.js') as f:
    js = f.read()

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": js
})
 
driver.get('https://wp.sharkshopping.com/programs_list')
# 必须等待一定的时间，不然会报错提示获取不到日志信息，因为絮叨等所有请求结束才能获取日志信息
time.sleep(60)
 
request_log = driver.get_log('performance')
# print(request_log)

data = pd.DataFrame()
for i in range(len(request_log)):
    message = json.loads(request_log[i]['message'])
    message = message['message']['params']
    # .get() 方式获取是了避免字段不存在时报错
    request = message.get('request')
    if(request is None):
        continue
 
    url = request.get('url')
    if 'api.sharkshopping.com/ec/api?method=tv.program.data' in url:
        # 得到requestId
        # print(message['requestId'])  # 1336.54
        # 通过requestId获取接口内容
        content = str(driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': message['requestId']}))
        res = requests.get(url)
        json_data = demjson.decode(res.text)
        # print(json_data)
        date_list = jsonpath(json_data, '$..real_date')
        del date_list[0]
        start_time_list = jsonpath(json_data, '$..start_time')
        end_time_list = jsonpath(json_data, '$..end_time')
        sku_list = jsonpath(json_data, '$..goods.sku')
        name_list = jsonpath(json_data, '$..goods.name')
        price_list = jsonpath(json_data, '$..goods.price')
        product_brand_list = jsonpath(json_data, '$..goods.product_brand')
        print(sku_list)
        
        start_time_list = [i for i in start_time_list if i != 0]
        end_time_list = [i for i in end_time_list if i != 0]

        print('date_list: ',len(date_list))
        print('start_time_list: ', len(start_time_list))
        print('end_time_list: ', len(end_time_list))
        print('sku_list: ', len(sku_list))
        print('name_list: ', len(name_list))
        print('price_list: ', len(price_list))
        print('product_brand_list: ', len(product_brand_list))

        list_content = [date_list,start_time_list,end_time_list,sku_list,name_list,price_list,product_brand_list]
        df = pd.DataFrame(list_content)
        df = df.T
        df.rename(columns={
                            0:'日期',
                            1:'开始时间（处理前）',
                            2:'结束时间（处理前）',
                            3:'商品编号',
                            4:'商品名称',
                            5:'价格',
                            6:'品牌名称',
                            },inplace=True)
        df['开始时间'] = df['开始时间（处理前）'].apply(lambda x:time.strftime("%H:%M",time.localtime(x)))
        df['结束时间'] = df['结束时间（处理前）'].apply(lambda x:time.strftime("%H:%M",time.localtime(x)))
        df['链接'] = 'https://wp.sharkshopping.com/product/' + df['商品编号']
        print(df)
        data = data.append(df)
driver.quit()

data.sort_values(by=['日期','开始时间'],ascending=True,inplace=True)  
data.drop_duplicates()
data.to_excel('./ghs.xlsx',sheet_name='ghs',index=False,columns=['日期','开始时间','结束时间','商品编号','商品名称','价格','品牌名称','链接'],encoding='utf-8')
print('Excel 文件保存成功！！')