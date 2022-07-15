import pandas as pd
import numpy as np
import xlwings as xw
import warnings
warnings.filterwarnings('ignore')

order_amt = float(input('输入购物公司订购额（单位：万元，保留一位小数）：')) 

df=pd.read_excel('./效率.xlsx',sheet_name='Sheet1')
target_file = './2022日报效率表（新）.xlsx'

df = df.apply(pd.to_numeric,errors='ignore')

# df['频道'] = df['频道'].fillna(method='ffill')
# df['播放日期'] = df['播放日期'].fillna(method='ffill')

df1 = df[ ( df['md名'] != '房产服务') & ( df['md名'] != '全装修工程') & ( df['md名'] != '汽车整车') & ( df['md名'] != '寿险')]
df1 = df1.reset_index(drop = True)

df1['播放开始小时']= df1['播放开始小时'].astype(int)
df1['商品播放开始时间'] = pd.to_datetime(df1['商品播放开始时间'])
df1 = df1 [ (df1['播放开始小时'] > 4 ) | (df1['播放开始小时'] == 0 )]
# df1 = df1 [~(df1['商品名称'].str.contains('订金'))]

df1 = df1[['频道','商品播放开始时间','商品名称','On-Air数量','On-Air金额','节目目标金额','边际利润额','边际利润目标','MD','PD','SH','希望播放（分）','播放类型']]
df1['节目达成率'] = df1['On-Air金额'] / df1['节目目标金额']
df1['边际利润达成率'] = df1['边际利润额'] / df1['边际利润目标']
df1['边际利润达成率'] = df1['边际利润达成率'].astype(str)
df1['边际利润达成率'] = df1['边际利润达成率'].str.replace('inf','0')
df1['边际利润达成率'] = df1['边际利润达成率'].astype(float)

df_live = df1 [ (df1['播放类型'] != '再播放')]
# df_live = df1.copy()
df_unlive = df1 [ (df1['播放类型'] == '再播放')]
  
df_best5 = df_live.sort_values(by = '节目达成率' , ascending= False ).reset_index(drop = True)
df_best5 = df_best5.iloc[:10,:]
df_best5 = df_best5[['频道','商品播放开始时间','商品名称','On-Air数量','On-Air金额','节目达成率','边际利润额','边际利润达成率']]

df_worst5 = df_live.sort_values(by = '节目达成率' , ascending= True ).reset_index(drop = True)
df_worst5 = df_worst5.iloc[:10,:]
df_worst5 = df_worst5[['频道','商品播放开始时间','商品名称','On-Air数量','On-Air金额','节目达成率','边际利润额','边际利润达成率']]

df_old = df1[df1['商品名称'].str.contains('暖心选')]
df_old = df_old.sort_values(by = '节目达成率' , ascending= False ).reset_index(drop = True)
df_old = df_old[['频道','商品播放开始时间','商品名称','On-Air数量','On-Air金额','节目达成率','边际利润额','边际利润达成率','MD','SH','PD','希望播放（分）','播放类型']] 

df_new_product = df1[df1['播放类型'] == '直播新商品']
df_new_product = df_new_product.sort_values(by = '节目达成率' , ascending= False ).reset_index(drop = True)
df_new_product = df_new_product[['频道','商品播放开始时间','商品名称','On-Air数量','On-Air金额','节目达成率','边际利润额','边际利润达成率','MD','SH','PD','希望播放（分）','播放类型']] 

df_old_live = df_live[(df1['商品名称'].str.contains('暖心选'))]
df_old_live_minutes = df_old_live['希望播放（分）'].sum()
df_old_live_amount = df_old_live['On-Air金额'].sum()

df_live_minutes = df_live['希望播放（分）'].sum()
df_live_amount = df_live['On-Air金额'].sum()

df_old_unlive = df_unlive[(df1['商品名称'].str.contains('暖心选'))]
df_old_unlive_minutes = df_old_unlive['希望播放（分）'].sum()
df_old_unlive_amount = df_old_unlive['On-Air金额'].sum()

df_unlive_minutes = df_unlive['希望播放（分）'].sum()
df_unlive_amount = df_unlive['On-Air金额'].sum()

df_repeat = pd.pivot_table(df1,index=['商品名称'],aggfunc={'商品播放开始时间':len,'On-Air金额':np.sum,'节目达成率':np.mean,'边际利润额':np.sum,'边际利润达成率':np.mean}).reset_index()
df_repeat = df_repeat[df_repeat['商品播放开始时间'] > 1]
df_repeat.rename(columns={'商品播放开始时间':'档数'},inplace=True)
df_repeat = df_repeat.sort_values(by = 'On-Air金额' , ascending= False ).reset_index(drop = True)
df_repeat = df_repeat[['商品名称','档数','On-Air金额','节目达成率','边际利润额','边际利润达成率']]                       

with pd.ExcelWriter(target_file) as writer:
    df_best5.to_excel(writer,sheet_name='达成率 best5', index=False)
    df_worst5.to_excel(writer,sheet_name='达成率 worst5', index=False)
    df_repeat.to_excel(writer,sheet_name='一日多档商品清单', index=False)
    df_old.to_excel(writer,sheet_name='暖心选清单', index=False)
    df_new_product.to_excel(writer,sheet_name='新品清单', index=False)
    
print('暖心选商品占直播时间比重 {:.1%},占直播贡献比重 {:.1%}'.format(df_old_live_minutes/df_live_minutes,df_old_live_amount/df_live_amount))
print('暖心选商品占节目带时间比重 {:.1%},占节目带贡献比重 {:.1%}\n'.format(df_old_unlive_minutes/df_unlive_minutes,df_old_unlive_amount/df_unlive_amount))

print('--------------------')
print('3. 双频on-air未税金额 {:.1f} 万，节目整体达成率 {:.0%}，占购物公司比重 {:.0%}；'.format(df1['On-Air金额'].sum()/10000,df1['On-Air金额'].sum()/df1['节目目标金额'].sum(),df1['On-Air金额'].sum()/10000*1.12/order_amt))
print('4. 节目 {}档，其中百万级 {}档，50万级 {}档，20万级 {}档，剩余 {}档；'.format(df1['商品名称'].count(),df1['On-Air金额'][df1['On-Air金额']  >= 1000000].count(),df1['On-Air金额'][(df1['On-Air金额']  >= 500000) & (df1['On-Air金额']  < 1000000) ].count(),df1['On-Air金额'][(df1['On-Air金额']  >= 200000) & (df1['On-Air金额']  < 500000) ].count(),df1['On-Air金额'][df1['On-Air金额']  < 200000 ].count()))
print('5. 直播 {}档，达百 {}档，70%到99% {}档，30%到69% {}档，30%以下 {}档；'.format(df_live['商品名称'].count(),df_live['节目达成率'][df_live['节目达成率'] >= 1].count(),df_live['节目达成率'][ (df_live['节目达成率'] >= 0.7) & (df_live['节目达成率'] < 1) ].count(),df_live['节目达成率'][ (df_live['节目达成率'] >= 0.3) & (df_live['节目达成率'] < 0.7) ].count(),df_live['节目达成率'][df_live['节目达成率'] < 0.3].count()))
print(f'6. 暖心选 {df_old.shape[0]}档，……')
print('--------------------')

app = xw.App(visible=False,add_book=False)
workbook = app.books.open('./2022日报效率表（新）.xlsx')
for i in workbook.sheets:
# 批量设置格式（行高、列宽、字体、大小、线框）
    value = i.range('A1').expand() # 选择要调整的区域
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
    value = i.range('A1:M1')  # 选择要调整的区域
    value.api.Font.Size = 10
    value.api.Font.Bold = True  # 设置为粗体
workbook.save()
workbook.close()
app.quit()

print(f'表格输出完成！！')