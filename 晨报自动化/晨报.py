# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 09:32:06 2021

@author: 2000102146
"""


import pandas as pd
import numpy as np
import xlwings as xw

df=pd.read_excel('D:/工作/【每日工作】/日报模板/效率表/效率原始表.xls',header=6)
target_file='D:/工作/【每日工作】/日报模板/效率表/日报效率表.xls'



df['频道'] = df['频道'].fillna(method='ffill')
df['播放日期'] = df['播放日期'].fillna(method='ffill')

df1 = df[ ( df['MD名'] != '房产服务') & ( df['MD名'] != '全装修工程') & ( df['MD名'] != '汽车整车') & ( df['MD名'] != '寿险')]
df1 = df1.reset_index(drop = True)

for i in range(len(df1['播放开始小时'])):
    df1['播放开始小时'][i] = int(df1['播放开始小时'][i])
    

df1 = df1 [ (df1['播放开始小时'] > 4 ) | (df1['播放开始小时'] == 0 )]
df1['直录播'] = df1['播放类型']
df1['直录播'] = df1['直录播'].replace(['次新品播放','直播重拍播放','直播新商品'],'直播')

df2 = df1.groupby(['频道', '直录播']).aggregate({'商品名称': 'count', 'On-Air数量':'sum', 'On-Air金额':'sum', 'On-Air利润':'sum', '节目目标金额':'sum'})
df2.loc['all'] = df2. apply ( lambda x: x. sum ())
df2['达成率']= df2['On-Air金额'] / df2['节目目标金额']
df2['毛利率']= df2['On-Air利润'] / df2['On-Air金额']
df2['平均单价']= df2['On-Air金额'] / df2['On-Air数量']


df3 = df1[ (df1['节目达成率'] >= 1 ) & ( df1['播放类型'] != '再播放')]

#B+专享节目
dfb = df1[(df1['频道'] == 12 ) & (df1['播放开始小时'] >= 19) & (df1['播放开始小时'] < 23) ]
dfb = dfb[['频道','商品播放时间','商品名称','On-Air数量', 'On-Air金额','节目达成率','On-Air净订购数量', 'MD','PD','SH']]   
dfb = dfb.sort_values(by = '节目达成率' , ascending= False ).reset_index(drop = True)



a = df1['直录播'][df1['直录播']=='直播'].count()
b = df1['节目达成率'][(df1['直录播'] =='直播' ) & (df1['节目达成率'] >= 1) ].count()
c = df1['节目达成率'][(df1['直录播'] =='直播' ) & (df1['节目达成率'] >= 0.7) & (df1['节目达成率'] < 1) ].count()
d = df1['节目达成率'][(df1['直录播'] =='直播' ) & (df1['节目达成率'] >= 0.3) & (df1['节目达成率'] < 0.7)].count()
e = df1['节目达成率'][(df1['直录播'] =='直播' ) & (df1['节目达成率'] < 0.3) ].count()

f = df1['On-Air金额'][df1['On-Air金额']  >= 1000000].count()
g = df1['On-Air金额'][(df1['On-Air金额']  >= 500000) & (df1['On-Air金额']  < 1000000) ].count()
h = df1['On-Air金额'][(df1['On-Air金额']  >= 200000) & (df1['On-Air金额']  < 500000) ].count()
i = df1['On-Air金额'][df1['On-Air金额']  < 200000 ].count()


print('--------------------')
print('节目整体达成率为：{:.1%}, 直播达成率为：{:.1%}, 录播达成率为：{:.1%}'.format(df2['达成率'][-1], df1['节目达成率'][df1['直录播']=='直播'].mean(), df1['节目达成率'][df1['直录播']=='再播放'].mean()))
print('昨日节目一共有{}档，其中百万级有{}档，50万级有{}档，20万级有{}档，剩余有{}档'.format( df1['直录播'].count(), f,g,h,i))
print('直播节目一共有{}档，其中达百的有{}档，70%到99%的有{}档，30%到69%的有{}档，30%一下的有{}档'.format(a,b,c,d,e))
print('B+专享节目共有{}档，平均达成率为{:.1%}'.format(dfb['节目达成率'].count(), dfb['节目达成率'].mean()))
print('--------------------')


writer=pd.ExcelWriter(target_file)

df1.to_excel(writer,sheet_name='数据表', index=False)
df2.to_excel(writer,sheet_name='达成率', index=True)
df3.to_excel(writer,sheet_name='达百直播', index=False)
dfb.to_excel(writer,sheet_name='B+专享', index=False)






writer.save()