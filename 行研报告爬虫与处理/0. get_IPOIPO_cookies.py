'''
# 获取一个session对象
import requests

headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            }

session = requests.Session()
main_url = 'http://ipoipo.cn/category-6.html' #推测对该url发起请求会产生cookie
session.get(main_url,headers=headers)
url = 'http://ipoipo.cn/post/12635.html'

page_text = session.get(url,headers=headers)
print(page_text)
print(requests.utils.dict_from_cookiejar(session.cookies))
'''


import time
from selenium import webdriver
import requests

# 自动登录
driver = webdriver.Chrome()
driver.get('http://ipoipo.cn/')
time.sleep(5)

# 获取cookie
cookies = driver.get_cookies()
cookies_list = []
for i in cookies:
    cookies_list.append(' '+i['name']+ '='+ i['value']) # 取出键值对，键值对前面都有一个空格，除了第一个键值对前面没有空格

cookiestr = ';'.join(cookies_list)
print(cookiestr)

headers ={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'Cookie':cookiestr[1:] # 开头的键值对并不需要前面的空格，如果有则会报错  可以将cookie保存到本地方便下次使用，注意有效时长问题

}

url = 'http://ipoipo.cn/post/12635.html'
response = requests.get(url,headers=headers).content.decode('utf-8')
# 成功输出登录后页面
print(response)

driver.quit()