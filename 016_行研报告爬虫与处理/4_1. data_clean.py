import pandas as pd
import os
import time
import xlwings as xw

t1 = time.time()

# 合并表格
output_path = './data_tables'
if not os.path.exists(output_path):
    os.makedirs(output_path)

df1 = pd.read_excel(os.path.join(output_path, '1. CBNData_data.xlsx'),sheet_name='CBNData')
df2 = pd.read_excel(os.path.join(output_path, '2. 199IT_data.xlsx'),sheet_name='199IT')
df3 = pd.read_excel(os.path.join(output_path, '3. IPOIPO_data.xlsx'),sheet_name='IPOIPO_final')

merge_df = pd.concat([df1,df2,df3])
merge_df['date'] = pd.to_datetime(merge_df['date'], format='%Y-%m-%d').dt.date

# 日期筛选
merge_df['year'] = pd.to_datetime(merge_df['date'], format='%Y-%m-%d').dt.year
merge_df['month'] = pd.to_datetime(merge_df['date'], format='%Y-%m-%d').dt.month
print(merge_df.info())

con1 = merge_df['month']==3
con2 = merge_df['month']==4
con3 = merge_df['year']==2021
merge_df = merge_df[(con1 | con2) & con3]

print('表格合并完成！!')

# （模糊）匹配分类
param_df = pd.read_excel(os.path.join(output_path, '0. 手动维护_模糊匹配参数表.xlsx'),sheet_name='table')
merge_df = pd.merge(merge_df,param_df,on='tags')
merge_df.drop(columns=['year','month','type'], axis=1, inplace=True)
merge_df = merge_df.sort_values(by='type_name')
merge_df = merge_df.rename(columns={
                                    'source': '来源',
                                    'date': '日期',
                                    'title':'标题',
                                    'category':'备注',
                                    'summary':'概述',
                                    'tags':'标签',
                                    'url':'链接',
                                    'type_name':'分类'
                                    })
merge_df.to_excel(os.path.join(output_path, '4. merge_data.xlsx'), sheet_name='merge', index=False, encoding='utf-8')
print('分类匹配完成！！')

# 自动化分页
data_list = list(merge_df['分类'].drop_duplicates()) # 去重处理
length = len(data_list) # 计算共有多少数量
output_file = os.path.join(output_path, '5. splited_data.xlsx')
with pd.ExcelWriter(output_file) as writer:
    count = 0
    for item in data_list:
        data_select = merge_df[merge_df['分类']==item] # 选出item对应的行
        data_select.to_excel(writer,sheet_name=item,index=False) # 按照对应的值生成 EXCEL 文件
        count += 1
        print('\rEXCEL表中共有 {} 个名称，正在拆分第 {} 个数据，拆分进度：{:.2%}'.format(length, count, count / length),end="")
print('\n{}个名称已经全部拆分完毕，请前往 5. splited_data.xlsx 文件中查看拆分后的各文件数据'.format(length))

t2 = time.time()

print('运行共耗时 {:.1f}秒'.format(t2 - t1))