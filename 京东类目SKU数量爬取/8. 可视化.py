import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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