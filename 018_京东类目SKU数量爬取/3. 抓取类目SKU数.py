import requests
from lxml import etree
import pandas as pd
import time
from alive_progress import alive_bar
import warnings
warnings.filterwarnings('ignore')

headers={
        'Content-Type':'application/json',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }

df = pd.read_excel('./2. 输出京东类目表.xlsx',sheet_name='result')
datas=[]
urls = df['小分类链接']
with alive_bar(len(urls)) as bar:   
    for url in urls:
        res = requests.get(url,headers=headers).text
        selector = etree.HTML(res)
        try:
            sku_count = selector.xpath('//*[@id="J_resCount"]/text()')[0]
        except IndexError:
            sku_count = '异常'
        data = {
                'url':url,
                'sku_count': sku_count.strip()
                }
        
        with open('SKU.txt','a') as f:
            f.write(str(data))
            
        datas.append(data)
        print(data)
        # time.sleep(3)
    
df_SKU = pd.DataFrame(datas)
df_result = pd.merge(df,df_SKU,left_on='小分类链接',right_on='url',how='inner')
df_result.to_excel('./4. 输出京东类目SKU原始数据.xlsx',sheet_name='result',index=False)
print('SKU数 爬取完成！！')