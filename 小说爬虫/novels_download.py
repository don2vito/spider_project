import requests
import time
import json
from pandas import DataFrame
import pprint
from lxml import etree
import re
import os
import random

headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',}

def get_url(url):
    res = requests.get(url,headers=headers)
    res.encoding='gbk'
    selector = etree.HTML(res.text)
    novel_urls = selector.xpath('//td[@class="ccss"]/a/@href')
    novel_names = selector.xpath('//td[@class="ccss"]/a/text()')
    for novel_name,novel_url in zip(novel_names,novel_urls):
        data = {
                'novel_name':novel_name.strip(),
                'novel_url':'https://www.wenku8.net/novel/1/1832/' + novel_url.strip(),
               }
        # print(novel_url.strip(),'https://www.wenku8.net/novel/1/1832/' + novel_url.strip())
        datas.append(data)
    return datas

def get_novel(url):
    res = requests.get(url, headers=headers)
    res.encoding = 'gbk'
    selector = etree.HTML(res.text)
    novle_title = selector.xpath('//*[@id="title"]/text()')[0]
    novel_body = selector.xpath('//*[@id="content"]/text()')
    body = '\n'.join(novel_body)
    txt_file = save_txt(novle_title,body)
    print(f'正在保存： {novle_title}')
    return txt_file

def save_txt(title,body):
    output_path = './sunqiqi_novels'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    file_name = title + '.txt'
    file_path = os.path.join(output_path, file_name)
    with open(file_path,'w+',encoding='utf-8') as f:
        f.write(body)
    return f


if __name__ == '__main__':
    url = 'https://www.wenku8.net/novel/1/1832/index.htm'
    datas = []
    datas = get_url(url)
    df = DataFrame(datas)
    for novel_url in df['novel_url']:
        get_novel(novel_url)
        time.sleep(random.randint(2,10))