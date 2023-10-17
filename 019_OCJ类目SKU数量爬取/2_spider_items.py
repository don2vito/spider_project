from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options 
import re
import pandas as pd
import time
import os
from alive_progress import alive_bar
import warnings
warnings.filterwarnings('ignore')

output_path = './data_list'
if not os.path.exists(output_path):
    os.makedirs(output_path)
df = pd.read_excel(os.path.join(output_path, 'catelog_list.xlsx'),sheet_name='catelog_list')

datas=[]
urls = df['小分类链接']
with alive_bar(len(urls)) as bar:   
    for url in urls:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        time.sleep(2)
        source = driver.page_source
        driver.quit()
        
        try:
            sku_count = re.findall('共(.*?)件商品',source,re.S)[0]
        except IndexError:
            sku_count = '异常'
        data = {
                'url':url,
                'sku_count': sku_count.strip()
                }
        
        with open('SKU.txt','a',encoding='utf-8') as f:
            f.write(str(data))
            
        datas.append(data)
        print(data)
        # time.sleep(3)
    
df_SKU = pd.DataFrame(datas)
df_result = pd.merge(df,df_SKU,left_on='小分类链接',right_on='url',how='inner')
df_result.to_excel('./3. 输出OCJ类目SKU原始数据.xlsx',sheet_name='result',index=False)
print('SKU数 爬取完成！！')