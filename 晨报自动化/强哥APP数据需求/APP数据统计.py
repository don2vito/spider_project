import pandas as pd
import os
import xlwings as xw
import warnings
warnings.filterwarnings('ignore')

df = pd.DataFrame()

for curDir, dirs, files in os.walk('./系统导出'): 
    for file in files:
        if file.endswith(".xlsx"):
            file_path = os.path.join(curDir, file)
            
            if 'SP' in file_path:
                file_path_SP = file_path
                df1 = pd.read_excel(file_path_SP,usecols=[2,3,4,5,6,7,8,14,15,17,18,23,24,28,36,37])
                df1 = df1.apply(pd.to_numeric,errors='ignore')
                df1['期间'] = file_path.split('\\')[-1].split('_')[0]
                df1['平台'] = 'SP'
            elif 'PAD' in file_path:
                file_path_PAD = file_path
                df1 = pd.read_excel(file_path_PAD,usecols=[2,3,4,5,6,7,8,14,15,17,18,23,24,28,36,37])
                df1 = df1.apply(pd.to_numeric,errors='ignore')
                df1['期间'] = file_path.split('\\')[-1].split('_')[0]
                df1['平台'] = 'PAD'
            elif 'PC' in file_path:
                file_path_PC = file_path
                df1= pd.read_excel(file_path_PC,usecols=[2,3,4,5,6,7,8,14,15,17,18,23,24,28,36,37])
                df1 = df1.apply(pd.to_numeric,errors='ignore')
                df1['期间'] = file_path.split('\\')[-1].split('_')[0]
                df1['平台'] = 'PC'
            elif 'B+' in file_path:
                file_path_B = file_path
                df1 = pd.read_excel(file_path_B,usecols=[2,3,4,5,6,7,8,14,15,17,18,23,24,28,36,37])
                df1 = df1.apply(pd.to_numeric,errors='ignore')
                df1['期间'] = file_path.split('\\')[-1].split('_')[0]
                df1['平台'] = 'B+'
                df1['订购数量'] = df1['订购数量'] * (-1)
                df1['订购金额'] = df1['订购金额'] * (-1)
                df1['取消数量'] = df1['取消数量'] * (-1)
                df1['取消金额'] = df1['取消金额'] * (-1)
                df1['出库数量'] = df1['出库数量'] * (-1)
                df1['出库金额'] = df1['出库金额'] * (-1)
                df1['配送完成数量'] = df1['配送完成数量'] * (-1)
                df1['配送完成金额'] = df1['配送完成金额'] * (-1)
                df1['销售数量'] = df1['销售数量'] * (-1)
                df1['销售金额'] = df1['销售金额'] * (-1)
                df1['销售利润'] = df1['销售利润'] * (-1)
                df1['拒收数量'] = df1['拒收数量'] * (-1)
                df1['拒收金额'] = df1['拒收金额'] * (-1)
            else:
                pass
            
            df = pd.concat([df,df1])
            period = file_path.split('\\')[-1].split('_')[0]
            
df_result = pd.pivot_table(df,
                           index=['期间','事业部名称','MD编号','MD名称'],
                           values=['订购数量','订购金额','取消数量','取消金额','出库数量','出库金额','配送完成数量','配送完成金额','销售数量','销售金额','销售利润','拒收数量','拒收金额'],
                           aggfunc='sum')
df_result['平台'] = 'APP'
df_result['取消率'] = df_result['取消金额'] / df_result['订购金额']
df_result['拒收率'] = df_result['拒收金额'] / df_result['出库金额']
df_result['转换率'] = df_result['销售金额'] / df_result['订购金额']
df_result['毛利率'] = df_result['销售利润'] / df_result['销售金额'] * 1.12
df_result = df_result.reset_index()
df_result = df_result[['期间','平台','事业部名称','MD编号','MD名称','订购数量','订购金额','取消数量','取消金额','取消率','出库数量','出库金额','配送完成数量','配送完成金额','销售数量','销售金额','转换率','销售利润','毛利率','拒收数量','拒收金额','拒收率']]

df_result.to_excel(f'./reslut_APP_{period}.xlsx',index=False,sheet_name='result')
print(f'\n表格处理完成…………')

app = xw.App(visible=False,add_book=False)
workbook = app.books.open(f'./reslut_APP_{period}.xlsx')

for i in workbook.sheets:
    # pbar.set_description(f'Processing {i}')
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
    # print(f'《{i.name}》 页面处理完成……')
workbook.save()
workbook.close()
app.quit()

print(f'\n表格输出完成！！')