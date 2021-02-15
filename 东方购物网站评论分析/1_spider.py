import requests
import pandas as pd
import time
from lxml import etree
import re
from pandas import DataFrame
import os

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0',
           'Connection':'keep-alive'
           }
datas = []
data2s = []

def get_cates_url(url):
    res = requests.get(url,headers=headers)
    res.encoding = 'utf-8'
    selector = etree.HTML(res.text)
    # result = etree.tostring(selector)
    # print(result)
    titles = selector.xpath('//div[@class="classificationListSmallBox"]/div[@class="classificationListSmallBoxTitle"]/a/text()')
    ids = selector.xpath('//div[@class="classificationListSmallBox"]/div[@class="classificationListSmallBoxTitle"]/a/@href')
    titles_ids = selector.xpath('//div[@class="classificationListSmallBoxContentList"]/div[@class="contents"]/div[@class="classificationbutton"]/a//@href')
    cates = selector.xpath('//div[@class="classificationListSmallBoxContentList"]/div[@class="contents"]/div[@class="classificationbutton"]/a/text()')
    cates_urls = selector.xpath('//div[@class="classificationListSmallBoxContentList"]/div[@class="contents"]/div[@class="classificationbutton"]/a/@href')
    # print(titles)
    # print(cates)
    # print(cates_urls)
    for titles_id,cate,cates_url in zip(titles_ids,cates,cates_urls):
        data={
                'title_id':titles_id.split('/')[-2],
                'cate':cate.strip(),
                'cate_id':cates_url.split('/')[-1],
                'cates_url':'http://www.ocj.com.cn' + cates_url.strip()
                }
        # print(cate.strip(),'http://www.ocj.com.cn' + cates_url.strip())
        datas.append(data)
    df1 = DataFrame(datas)
    for title,id in zip(titles,ids):
        data2={
                'title':title.strip(),
                'id':id.split('/')[-1]
                }
        data2s.append(data2)
    df2 = DataFrame(data2s)
    df_result = pd.merge(df1, df2, how='left', left_on='title_id',right_on='id')
    return df_result

if __name__ == '__main__':
    # 步骤一：爬取分类表
    cat_url = 'http://www.ocj.com.cn/allCategories'
    df_result = get_cates_url(cat_url)
    output_path = './data_list'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    df_result.to_excel(os.path.join(output_path, 'catelog_list.xlsx'),sheet_name='catelog_list',index=False,columns=['title','title_id','cate','cate_id','cates_url'],encoding='utf-8')
    # print(df_result.head())
    print('《分类表》爬取完成！！\n')