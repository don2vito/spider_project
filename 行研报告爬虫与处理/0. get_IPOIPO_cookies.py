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
from time import sleep
from selenium import webdriver

# 自动登录
driver = webdriver.Chrome(executable_path='chromedriver.exe')
driver.get('https://qzone.qq.com/')
# driver.set_window_position(20, 40)
# driver.set_window_size(1100,700)
# 表单在该框架下
driver.switch_to_frame('login_frame')
sleep(0.5)
driver.find_element_by_xpath('//*[@id="bottom_qlogin"]/a[1]').click()
driver.find_element_by_xpath('//*[@id="u"]').send_keys('XXXX') # 你的QQ号
driver.find_element_by_xpath('//*[@id="p"]').send_keys('XXXXX')# 你的QQ密码
driver.find_element_by_xpath('//*[@id="login_button"]').click()
''！！！！如果输入账号密码后 弹出滑动验证码则可以这样执行
方式一：input('手动验证后输入空格继续：)
方式二： 将滑块图片保存下来 交给云打码平台，算出 X Y距离后 使用selenium动作链模拟人为验证进行登录
关于验证码识别，下一期在详解
！！！''
# 获取cookie
cookies = driver.get_cookies()
cookies_list = []
for i in cookies:
    cookies_list.append(' '+i['name']+ '='+ i['value']) # 取出键值对，键值对前面都有一个空格，除了第一个键值对前面没有空格

cookiestr = ';'.join(cookies_list)

headers ={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'Cookie':cookiestr[1:] # 开头的键值对并不需要前面的空格，如果有则会报错  可以将cookie保存到本地方便下次使用，注意有效时长问题

}

url = 'https://user.qzone.qq.com/XXXXX' # 你的QQ号
response = requests.get(url,headers=headers).content.decode('utf-8')
# 成功输出登录后页面
print(response)
————————————————
版权声明：本文为CSDN博主「跟着上帝去流浪」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/qq_39915318/article/details/105881809
'''