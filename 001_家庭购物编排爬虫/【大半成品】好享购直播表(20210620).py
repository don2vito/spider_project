from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import pprint
from lxml import etree
from pandas import DataFrame
import json

def scroll_until_loaded():
    check_height = driver.execute_script("return document.body.scrollHeight;")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(driver, 20).until(lambda driver: driver.execute_script("return document.body.scrollHeight;") > check_height)
            check_height = driver.execute_script("return document.body.scrollHeight;")
        except TimeoutException:
            break

url = 'https://m.hao24.com/live/yesterday.html'

driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)

# element = driver.find_element_by_xpath('//*[@id="thelist"]/li[1]/a/div[2]/p[2]')
# ActionChains(driver).move_to_element(element).perform()
# time.sleep(2)

# scroll_until_loaded()
js = "window.scrollTo(0,document.body.scrollHeight)"
driver.execute_script(js)
time.sleep(30)

source = driver.page_source
# pprint.pprint(source)
driver.quit()

selector = etree.HTML(source)

datas=[]

date_times = selector.xpath('//*[@id="thelist"]/li/a/div[2]/p[1]/span[1]/text()')
titles = selector.xpath('//*[@id="thelist"]/li/a/div[2]/p[2]/text()')
prices = selector.xpath('//*[@id="thelist"]/li/a/div[2]/p[3]/text()')
links = selector.xpath('//*[@id="thelist"]/li/a/@href')
print(len(date_times))
for date_time, title, price, link in zip(date_times, titles, prices, links):
    data = {
        'b_time': date_time.strip().split('-')[0],
        'e_time': date_time.strip().split('-')[1],
        'id': link.strip().split('/')[-1].split('.')[0],
        'title': title.strip(),
        'price': price.strip(),
        'link': link.strip()
    }

    # print(data)
    print(date_time.strip().split('-')[0], date_time.strip().split('-')[1], link.strip().split('/')[-1].split('.')[0],
          title.strip(), price.strip(), link.strip())
    datas.append(data)

df=DataFrame(datas)
df.sort_values(by=['b_time'],ascending=[True],inplace=True)
df['price'] = df['price'].str.replace('￥','').replace(' ','')
df.to_excel(r'./hao24.xlsx',sheet_name='hao24',index=False,columns=['b_time','e_time','id','title','price','link'],encoding='utf-8')
print('Excel 已生成！！')