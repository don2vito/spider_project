from selenium import webdriver
import time,pandas as pd,re,json
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

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

__browser_url = r'D:\360\360se6\Application\360se.exe'  # 360浏览器的地址  
chrome_options.binary_location = __browser_url  

driver = webdriver.Chrome(chrome_options=chrome_options)

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
        print(message['requestId'])  # 1336.54
        # 通过requestId获取接口内容
        content = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': message['requestId']})
        print(url)
        print(content)
driver.quit()