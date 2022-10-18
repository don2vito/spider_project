#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from alive_progress import alive_bar
import xlwings as xw
import warnings

warnings.filterwarnings('ignore')


# In[2]:


df=pd.read_excel('./效率_月累计.xlsx',sheet_name='Sheet1')
target_file = './结果表.xlsx'

df = df.apply(pd.to_numeric,errors='ignore')


# In[3]:


df['播放开始小时']= df['播放开始小时'].astype(int)
df['播放日期'] = pd.to_datetime(df['播放日期'])
df = df[ ( df['md名'] != '房产服务') & ( df['md名'] != '全装修工程') & ( df['md名'] != '汽车整车') & ( df['md名'] != '寿险')]
df = df [ (df['播放开始小时'] > 4 ) | (df['播放开始小时'] == 0 )]


# In[4]:


df = df[['播放日期','频道','On-Air金额','On-Air利润','希望播放（分）']]
df['频道'] = df['频道'].str.replace('频道','')
df['频道'] = df['频道'].astype('int')


# In[5]:


df_group = df.groupby(['播放日期','频道'])['On-Air金额','On-Air利润','希望播放（分）'].sum().reset_index()
df_group = df_group[df_group['播放日期']==max(df_group['播放日期'])]
df_sum = df_group.sum()
df_sum['播放日期'] = np.nan
df_sum['频道'] = np.nan
df_sum = pd.DataFrame(df_sum[['播放日期','频道','On-Air金额','On-Air利润','希望播放（分）']]).T
df_result = pd.concat([df_group ,df_sum])
df_result['分钟订购'] = (df_result['On-Air金额'] / df_result['希望播放（分）']).round(0)
df_result['分钟利润'] = (df_result['On-Air利润'] / df_result['希望播放（分）']).round(0)
df_result['频道'] = df_result['频道'].astype('float')
df_result['播放日期'] = pd.to_datetime(df_result['播放日期'],format='%Y=%m-%d')
df_result['播放日期'] = df_result['播放日期'].astype('str')[:10]
df_result = df_result[['播放日期','频道','分钟订购','分钟利润']]


# In[6]:


df_group2 = df.groupby(['频道'])['On-Air金额','On-Air利润','希望播放（分）'].sum().reset_index()
df_sum2 = df_group2.sum()
df_sum2['频道'] = np.nan
df_sum2 = pd.DataFrame(df_sum2[['频道','On-Air金额','On-Air利润','希望播放（分）']]).T
df_result2 = pd.concat([df_group2 ,df_sum2])
df_result2['分钟订购'] = (df_result2['On-Air金额'] / df_result2['希望播放（分）']).round(0)
df_result2['分钟利润'] = (df_result2['On-Air利润'] / df_result2['希望播放（分）']).round(0)
df_result2['频道'] = df_result2['频道'].astype('float')
df_result2 = df_result2[['频道','分钟订购','分钟利润']]


# In[7]:


with pd.ExcelWriter(target_file) as writer:
    df_result.to_excel(writer,sheet_name='当天', index=False)
    df_result2.to_excel(writer,sheet_name='月累计', index=False)


# In[8]:


app = xw.App(visible=False,add_book=False)
workbook = app.books.open('./结果表.xlsx')

with alive_bar(len(workbook.sheets)) as bar:    
    for i in workbook.sheets:
        bar()
        # pbar.set_description(f'Processing {i}')
    # 批量设置格式（行高、列宽、字体、大小、线框）
        a4_range=i.range('A4')
        a4_range.value='合计'
        value = i.range('A1').expand('table')# 选择要调整的区域
        value.rows.autofit() # 调整列宽字符宽度
        value.columns.autofit()  # 调整行高字符宽度
        value.api.Font.Name = '微软雅黑' # 设置字体
        value.api.Font.Size = 9 # 设置字号大小（磅数）
        value.api.VerticalAlignment = xw.constants.VAlign.xlVAlignCenter # 设置垂直居中
        value.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter # 设置水平居中
        for cell in value:
            for b in range(7,12):
                cell.api.Borders(b).LineStyle = 1 # 设置单元格边框线型
                cell.api.Borders(b).Weight = 2 # 设置单元格边框粗细
        value = i.range('A1').expand('right')  # 选择要调整的区域
        value.api.Font.Size = 10
        value.api.Font.Bold = True  # 设置为粗体
        # print(f'《{i.name}》 页面处理完成……')
workbook.save()
workbook.close()
app.quit()

print(f'\n表格输出完成！！')

