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


driver=webdriver.Chrome('./exe/chromedriver.exe', options=chrome_options,desired_capabilities=caps)


# 简单隐藏selenium特征
with open('./stealth.min.js') as f:
    js = f.read()

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
  "source": js
})




###############################################################



# 获取性能日志数据，根据request url 查询requestId
# url示例：pangu.ocj.com.cn/api/bom/item/product/ProductQueryFacade/list
logs = driver.get_log("performance")



# 根据requestId  获取responseBody
driver.execute_cdp_cmd('Network.getResponseBody',{'requestId': '14796.106'})



# 性能日志参考
'''
{'method': 'Network.requestWillBeSent',
 'params': {'documentURL': 'http://pangu.ocj.com.cn/product/index.html',
            'frameId': 'EF39E2870D866ECE80E15B8CB3F2F8E3',
            'hasUserGesture': False,
            'initiator': {'stack': {'callFrames': [{'columnNumber': 21998,
                                                    'functionName': 'r.<computed>',
                                                    'lineNumber': 0,
                                                    'scriptId': '468',
                                                    'url': 'https://retcode.alicdn.com/retcode/bl.js'},
                                                   {'columnNumber': 123986,
                                                    'functionName': 'post',
                                                    'lineNumber': 14,
                                                    'scriptId': '233',
                                                    'url': 'https://frontendonline-erp.ocj.com.cn/common/v0.0.9/ocj.js'},
                                                   {'columnNumber': 46606,
                                                    'functionName': '',
                                                    'lineNumber': 0,
                                                    'scriptId': '507',
                                                    'url': 'https://frontendonline-erp.ocj.com.cn/product/v1.7.4/js/pages/productList.js'},
                                                   {'columnNumber': 4635,
                                                    'functionName': 'u',
                                                    'lineNumber': 6,
                                                    'scriptId': '499',
                                                    'url': 'https://frontendonline-erp.ocj.com.cn/portal/v1.0.6/js/components.js'},
                                                   {'columnNumber': 4423,
                                                    'functionName': '',
                                                    'lineNumber': 6,
                                                    'scriptId': '499',
                                                    'url': 'https://frontendonline-erp.ocj.com.cn/portal/v1.0.6/js/components.js'},
                                                   {'columnNumber': 5057,
                                                    'functionName': 'e.<computed>',
                                                    'lineNumber': 6,
                                                    'scriptId': '499',
                                                    'url': 'https://frontendonline-erp.ocj.com.cn/portal/v1.0.6/js/components.js'},
                                                   {'columnNumber': 62285,
                                                    'functionName': 'o',
                                                    'lineNumber': 0,
                                                    'scriptId': '503',
                                                    'url': 'https://frontendonline-erp.ocj.com.cn/product/v1.7.4/js/app.js'},
                                                   {'columnNumber': 62480,
                                                    'functionName': 's',
                                                    'lineNumber': 0,
                                                    'scriptId': '503',
                                                    'url': 'https://frontendonline-erp.ocj.com.cn/product/v1.7.4/js/app.js'}]},
                          'type': 'script'},
            'loaderId': 'E87B54F4746AAC7A2BC26B0435544026',
            'request': {'hasPostData': True,
                        'headers': {'Content-Type': 'application/json',
                                    'EagleEye-SessionID': 'UskO9sORu276kX8w41g09a49938n',
                                    'EagleEye-TraceID': '110b391a163005762550210059c558',
                                    'EagleEye-pAppName': 'h228fiskcr@273ef19c3f9c558',
                                    'Referer': 'http://pangu.ocj.com.cn/product/index.html',
                                    'User-Agent': 'Mozilla/5.0 (Macintosh; '
                                                  'Intel Mac OS X 10_15_7) '
                                                  'AppleWebKit/537.36 (KHTML, '
                                                  'like Gecko) '
                                                  'Chrome/86.0.4240.198 '
                                                  'Safari/537.36',
                                    'authCode': 'production_management',
                                    'source': '1',
                                    'token': 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDY1NzciLCJhY2NvdW50SWQiOiIxMDY1NzciLCJzdGFmZlVzZXJJZCI6IjEyNjcyNCIsImlzcyI6Im9jai1zdGFyc2t5IiwiZXhwIjoxNjMwMDcyMDIzLCJpYXQiOjE2MzAwNTc2MjN9.hTic_aH7qZxGxwh0oZ8iypLGlUTwCMSFVFv7e-6oEKk'},
                        'initialPriority': 'High',
                        'method': 'POST',
                        'mixedContentType': 'none',
                        'postData': '{"page":{"pageNo":1,"pageSize":10},"startTime":"2020-08-27 '
                                    '00:00:00","endTime":"2021-08-27 '
                                    '23:59:59"}',
                        'postDataEntries': [{'bytes': 'eyJwYWdlIjp7InBhZ2VObyI6MSwicGFnZVNpemUiOjEwfSwic3RhcnRUaW1lIjoiMjAyMC0wOC0yNyAwMDowMDowMCIsImVuZFRpbWUiOiIyMDIxLTA4LTI3IDIzOjU5OjU5In0='}],
                        'referrerPolicy': 'strict-origin-when-cross-origin',
                        'url': 'http://pangu.ocj.com.cn/api/bom/item/product/ProductQueryFacade/list'},
            'requestId': '14796.106',
            'timestamp': 7121.085586,
            'type': 'Fetch',
            'wallTime': 1630057625.502553}}
'''