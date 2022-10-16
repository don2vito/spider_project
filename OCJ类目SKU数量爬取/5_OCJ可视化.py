import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np

df = pd.read_excel('./4. 输出OCJ类目SKU清洗后数据1015.xlsx',sheet_name='result')
df['整体'] = '整体'

df_OCJ = df.groupby(['整体','大分类', '中分类',])['sku_count'].sum().reset_index().sort_values(by='sku_count',ascending=False)
df_OCJ['SKU数占比%'] = ((df_OCJ['sku_count'] / df_OCJ['sku_count'].sum()) * 100).round(1) 
df_OCJ.rename(columns={'sku_count':'转换后SKU数'}, inplace = True)
df_OCJ['公司'] = 'OCJ'
df_OCJ = df_OCJ[['整体','大分类', '中分类','转换后SKU数']]

# OCJ 树状图

fig1 = px.treemap(df_OCJ, 
                 path=['整体','大分类', '中分类'], 
                 values='转换后SKU数', 
                 title='东购类目SKU占比树状图',
                 # color='转换后SKU数',
                 # color_continuous_scale='RdBu',
                 # color_continuous_midpoint=df1['转换后SKU数'].mean()
                )
fig1.update_traces(textinfo='label+value',textfont = dict(size = 20))                                                                                 
pio.write_html(fig1,'东购类目SKU占比树状图.html')
pio.write_image(fig1,'东购类目SKU占比树状图.png','png',width=1400,height=800)


df2 = pd.read_excel('./【资料】新媒体商品20220915-10148.xlsx',sheet_name='Sheet1')
df2 = df2[df2['订购数量']>0]
df2['订购单价'] = df2['订购金额'] / df2['订购数量']

#  JD 热力图
bins = [0,200,300,500,700,1000,2000,3000,5000,10000,99999999999]
groups1 = ['2百','3百','5百','7百','1千','2千','3千','5千','1万','1万以上']
bins2 = [0,10,20,30,40,50,60,70,80,90,999]
groups2 = [.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0]
df2['单价级别'] = pd.cut(df2['订购单价'],bins,labels=groups1)

data = df2.groupby(['大分类名称','单价级别'])['商品名称'].count().reset_index()
data = pd.pivot(data,values='商品名称',index='大分类名称',columns='单价级别')
data = data.div(data.sum(axis=1), axis=0)
data = data.apply(lambda x:round(x * 100,1))

data2 = data.apply(lambda x:pd.cut(x,bins2,labels=groups2))
data2 = data2.fillna(.1)

# data = data.applymap(lambda x:str(round(x / 10000,2)) + ' 万')

x = list(data.columns)
y = list(data.index)
z = data2.values.tolist()
z_text = data.fillna('').values.tolist()

#  自定义色卡
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
                                   # colorscale='Plotly3'
                                    colorscale=colorscale
                                   )
# 字体大小设置
for i in range(len(fig2.layout.annotations)):
    fig2.layout.annotations[i].font.size=20
fig2.update_layout(title='东购类目SKU(%)占比热力图')
fig2.update_xaxes(side='top',tickfont={'size': 18})
fig2.update_yaxes(tickfont={'size': 18})
pio.write_html(fig2,'东购类目SKU占比(%)热力图.html')
pio.write_image(fig2,'东购类目SKU占比(%)热力图.png','png',width=1400,height=800)
