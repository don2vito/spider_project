import requests
import json
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

headers={
        'Content-Type':'application/json',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }

url = 'https://dc.3.cn/category/get'
res = requests.get(url,headers=headers)
# 把传递过来的信息GBK进行解码
res.encoding='GBK'
json_data=json.loads(res.text)
# 取出"data" 键中分类列表
categorys = json_data['data']


def get_category_item(category_info):
    # 使用 `|` 分割类型信息字符串
    categorys =   category_info.split('|')
    # 类别的名称
    category_name = categorys[1]
    # 类别的URL
    category_url = categorys[0]
    # 获取 category_url 中 `-` 个数
    count = category_url.count('-')

    if category_url.count('jd.com') != 0:
        # 其他就是本身就是URL, 前面补一个协议头
        category_url = 'https://' + category_url
    elif count == 1:
        # 如果包含一个 '-' 是二级分类的频道
        category_url = 'https://channel.jd.com/{}.html'.format(category_url)
    else:
        # 如果包含2个 '-' 是三级分类的列表
        # 1. 把 `-` 替换为 ','
        category_url = category_url.replace('-', ',')
        # 2. 生成具体列表的URL
        category_url = 'https://list.jd.com/list.html?cat={}'.format(category_url)
    return category_name, category_url


result = pd.DataFrame()
df = dict()
# 遍历分类列表
for category in categorys:
    # 获取大分类,包含子分类; 注: 第一层的分类都在在0索引上;
    b_category = category['s'][0]
    # 获取大分类信息(分类URL,名称)
    b_category_info =  b_category['n']
    # 解析大分类信息, 获取大分类名称和URL
    df['大分类名'], df['大分类链接'] = get_category_item(b_category_info)

    # 获取中分类列表
    m_category_s =  b_category['s']

    # 遍历第二层分类列表
    for m_category in m_category_s:
        # 获取中分类信息
        m_category_info = m_category['n']
        df['中分类名'], df['中分类链接'] = get_category_item(m_category_info)
        # 获取小分类列表
        s_category_s = m_category['s']
        # 遍历小分类分类列表
        for s_category in s_category_s:
            # 获取第三层分类名称
            s_category_info = s_category['n']
            # 获取三级分类信息
            df['小分类名'], df['小分类链接'] = get_category_item(s_category_info)
            print('{} 已爬取……'.format(df['小分类名']))
            table = pd.DataFrame.from_dict(df,orient='index').T
            result = pd.concat([result, table])
result.to_excel('./2. 输出京东类目表.xlsx',sheet_name='result',index=False)
print('爬取成功！！')