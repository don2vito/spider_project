import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np


df1 = pd.read_excel('./6. 输出京东类目SKU转换后数据.xlsx',sheet_name='result')

df_JD = df1.groupby('映射东购事业部')['转换后SKU数'].sum().reset_index().sort_values(by='转换后SKU数',ascending=False)
df_JD['SKU数占比%'] = ((df_JD['转换后SKU数'] / df_JD['转换后SKU数'].sum()) * 100).round(1) 
df_JD['公司'] = 'JD'
df_JD = df_JD[['公司','映射东购事业部','转换后SKU数','SKU数占比%']]
df_JD.loc[len(df_JD.index)] = ['JD', '商城商品事业部', 0, 0.0]

df2 = pd.read_excel('./【资料】2022年购物公司商品0101-1013.xlsx',sheet_name='Sheet1')
df2 = df2[df2['订购数量']>0]

df_OCJ = df2.groupby('事业部')['商品编号'].count().reset_index().sort_values(by='商品编号',ascending=False)
df_OCJ['SKU数占比%'] = ((df_OCJ['商品编号'] / df_OCJ['商品编号'].sum()) * 100).round(1) 
df_OCJ.rename(columns={'事业部':'映射东购事业部', '商品编号':'转换后SKU数'}, inplace = True)
df_OCJ['公司'] = 'OCJ'
df_OCJ = df_OCJ[['公司','映射东购事业部','转换后SKU数','SKU数占比%']]
df_OCJ.loc[len(df_OCJ.index)] = ['OCJ', 0, 0, 0.0]
df_OCJ.loc[len(df_OCJ.index)] = ['OCJ', '团购', 0, 0.0]

df_concat = pd.concat([df_JD,df_OCJ])

# SKU类目占比对比（柱状图）
fig = px.bar(df_concat, x='映射东购事业部', y='SKU数占比%',barmode='group',color='公司',text='SKU数占比%')
fig.update_layout(title='事业部SKU占比对比(%)')
fig.update_traces(textposition='outside',textfont_size=16,textfont_color=['#FC5531'])
pio.write_html(fig,'事业部SKU占比对比.html')
pio.write_image(fig,'事业部SKU占比对比.png','png',width=1400,height=800)


# JD 树状图
df1['整体'] = '整体'
fig1 = px.treemap(df1, 
                 path=['整体', '大分类名', '中分类名'], 
                 values='转换后SKU数', 
                 title='京东类目SKU占比树状图',
                 # color='转换后SKU数',
                 # color_continuous_scale='RdBu',
                 # color_continuous_midpoint=df1['转换后SKU数'].mean()
                )
fig1.update_traces(textinfo='label+value',textfont = dict(size = 20))                                                                                 
pio.write_html(fig1,'JD类目SKU占比树状图.html')
pio.write_image(fig1,'JD类目SKU占比树状图.png','png',width=1400,height=800)


#  JD 热力图
bins = [0,1,3000,8000,20000,50000,100000,250000,500000,700000,99999999999]
groups1 = ['0','3千','8千','2万','5万','10万','25万','50万','70万','70万以上']
bins2= [0,10,20,30,40,50,60,70,80,90,999]
groups2 = [.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0]
df1['SKU数级别'] = pd.cut(df1['转换后SKU数'],bins,labels=groups1)
df1['SKU数级别'] = df1['SKU数级别'].fillna('0')

data = df1.groupby(['大分类名','SKU数级别'])['转换后SKU数'].count().reset_index()
data = pd.pivot(data,values='转换后SKU数',index='大分类名',columns='SKU数级别')
data = data.div(data.sum(axis=1), axis=0)
data = data.apply(lambda x:round(x * 100,1))
data.rename(index={'男装':'男女装'},inplace=True)

data2 = data.apply(lambda x:pd.cut(x,bins2,labels=groups2))
data2 = data2.fillna(.1)

# data = data.applymap(lambda x:str(round(x / 10000,2)) + ' 万')

data.drop(index='众筹',columns='0',inplace=True)
data2.drop(index='众筹',columns='0',inplace=True)

x = list(data.columns)
y = list(data.index)
z = data2.values.tolist()
z_text = data.fillna('').values.tolist()

# 自定义色卡
colorscale = [[0.0,'rgb(0,153,102)'],
              [.2,'rgb(211,207,99)'],
              [.4,'rgb(255,153,51)'],
              [.6,'rgb(204,97,51)'],
              [.8,'rgb(102,0,153)'],
              [1.0,'rgb(126,0,35)']]

fig2 = ff.create_annotated_heatmap(z,
                                   x=x,
                                   y=y,
                                   annotation_text=z_text,
                                   colorscale=colorscale
                                   )
# 字体大小设置
for i in range(len(fig2.layout.annotations)):
    fig2.layout.annotations[i].font.size=20
fig2.update_layout(title='JD类目SKU(%)占比热力图')
fig2.update_xaxes(side='top',tickfont={'size': 18})
fig2.update_yaxes(tickfont={'size': 18})
pio.write_html(fig2,'JD类目SKU占比热力图.html')
pio.write_image(fig2,'JD类目SKU占比热力图.png','png',width=1400,height=800)