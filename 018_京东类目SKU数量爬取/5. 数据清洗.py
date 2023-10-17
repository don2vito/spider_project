import pandas as pd
import xlwings as xw
import warnings
warnings.filterwarnings('ignore')

df = pd.read_excel('./4. 输出京东类目SKU原始数据.xlsx',sheet_name='result')

def transform(a,b):
    if a == '万':
        return float(b) * 10000
    elif a == '异常':
        return 0
    else:
        return float(b)

df['基数'] = df['SKU数'].str.findall('[0-9.]').str.join('')
df['单位'] = df['SKU数'].str.findall('[\u4e00-\u9fa5 ；()]').str.join('')
df['转换后SKU数'] = df.apply(lambda x :transform(x['单位'],x['基数']), axis=1)
df = df[['大分类名', '大分类链接', '中分类名', '中分类链接', '小分类名', '小分类链接','转换后SKU数']]
df.to_excel('./6. 输出京东类目SKU转换后数据.xlsx',sheet_name='result',index=False)

app = xw.App(visible=False,add_book=False)
workbook = app.books.open('./6. 输出京东类目SKU转换后数据.xlsx')

for i in workbook.sheets:
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
    value = i.range('A1').expand('right')  # 选择要调整的区域
    value.api.Font.Size = 10
    value.api.Font.Bold = True  # 设置为粗体
    # print(f'《{i.name}》 页面处理完成……')
workbook.save()
workbook.close()
app.quit()

print('数据清洗完成！！')