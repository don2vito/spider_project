import os
import time
import xlwings as xw


# 美化格式、排版布局
t1 = time.time()

output_path = './data_tables'
if not os.path.exists(output_path):
    os.makedirs(output_path)
    
pic_path = './pic_output'
if not os.path.exists(pic_path):
    os.makedirs(pic_path)

app = xw.App(visible=False,add_book=False)
workbook = app.books.open(os.path.join(output_path, '5. splited_data.xlsx'))
for i in workbook.sheets:
# 批量删除“分类”列
    i.api.Columns(8).Delete() # 删除列

# 批量设置格式（行高、列宽、字体、大小、线框）
    value = i.range('A1').expand() # 选择要调整的区域
    value.column_width = 30 # 调整列宽字符宽度
    value.column_height = 30  # 调整行高字符宽度
    value.api.Font.Name = '微软雅黑' # 设置字体
    value.api.Font.Size = 9 # 设置字号大小（磅数）
    value.api.VerticalAlignment = xw.constants.VAlign.xlVAlignCenter # 设置垂直居中
    for cell in value:
        for b in range(7,12):
            cell.api.Borders(b).LineStyle = 1 # 设置单元格边框线型
            cell.api.Borders(b).Weight = 2 # 设置单元格边框粗细
    value = i.range('A1:G1')  # 选择要调整的区域
    value.api.Font.Size = 10

# 批量添加首行与格式
    i.api.Rows(1).Insert()  # 插入首行
    i.range('A1').value = '《' + i.name + '》 行研报告汇总'  # 写入单元格
    value = i.range('A1:G1')  # 选择要调整的区域
    value.api.Font.Name = '微软雅黑'  # 设置字体
    value.api.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter # 设置水平居中
    value.color = (49, 134, 155)  # 设置单元格的填充颜色【RGB】
    # value.api.Font.Color = '#000000'  # 设置字体的颜色（白色）【十六进制】
    value.api.Font.ColorIndex = 2 # 白色（参考 VBA 的色系对应表）
    value.api.Font.Size = 16  # 设置字体的大小
    value.api.Font.Bold = True  # 设置为粗体
    print('《' + i.name + '》 正在被处理中...')
    i.range('A1:G1').api.merge()  # 合并单元格
    
# 插入词云图
    pic_name = i.name + '.png'
    pic = os.path.join(r'D:\MyProject\spider\行研报告爬虫与处理\pic_output', pic_name)
    i.pictures.add(pic,left=i.range('K1').left,top=i.range('K1').top,width=300,height=300)
    print(f'《{i.name}》词云图 已添加入 EXCEL 中！！')

workbook.save()
workbook.close()
app.quit()
print('格式调整完毕！！')

t2 = time.time()

print('运行共耗时 {:.1f}秒'.format(t2 - t1))