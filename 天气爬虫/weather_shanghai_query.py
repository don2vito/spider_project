import pandas as pd
import os
import csv

b_year =  int(input('输入起始年份：'))
b_month = int(input('输入起始月份：'))
e_month = int(input('输入结束月份：'))
b_date = str(b_year) + str(b_month)
e_date = str(b_year) + str(e_month)

list_path = './weather_shanghai_spider/table_list'
if not os.path.exists(list_path):
    os.makedirs(list_path)

for month in range(0, e_month - b_month + 1):
    day = str(b_year) + str(b_month + month)
    if (b_month + month) < 10:
        month1 = '0' + str(b_month + month)
        year1 = str(b_year)
    elif (b_month + month) == 13:
        month1 = str('1')
        year1 = str(b_year + 1)
    else:
        month1 = str(b_month + month)
        year1 = str(b_year)
    subscribeTime = str(year1) + str(month1)
    url = 'http://www.tianqihoubao.com/lishi/shanghai/month/' + subscribeTime + '.html'
    data = pd.read_html(url,encoding='gbk',header=0)[0]
    # print(data)
    file_name = '上海天气数据' + '(' + subscribeTime + ').xlsx'
    data.to_excel(os.path.join(list_path,file_name),index=False,encoding='utf-8', header=True,sheet_name='weather_shanghai',columns=['日期','天气状况','气温','风力风向'])
    print('共生成数据{}行，{}列'.format(data.shape[0], data.shape[1]))
    print(subscribeTime + '  天气爬取成功！！')

file_names = os.listdir(list_path)
frames = []
for file_name in file_names:
    path = os.path.join(list_path,file_name)
    df = pd.read_excel(path,encoding='utf-8',header=0,sheet_name='weather_shanghai',columns=['日期','天气状况','气温','风力风向'])
    # print(df.head())
    frames.append(df)
# print(frames)
result = pd.concat(frames,join_axes=[df.columns])
# print(result.head())
file_name = '上海天气数据' + '(' + file_names[0].split('(')[-1].split(')')[0] + '-' + file_names[-1].split('(')[-1].split(')')[0] + ').xlsx'
output_path = './weather_shanghai_spider/merge'
if not os.path.exists(output_path):
    os.makedirs(output_path)
output_file_path = os.path.join('./weather_shanghai_spider/merge',file_name)
result.to_excel(output_file_path,index=False,encoding='utf-8', header=True,sheet_name='weather_shanghai',columns=['日期','天气状况','气温','风力风向'])
print('共生成数据{}行，{}列'.format(result.shape[0],result.shape[1]))
print('合并天气数据 成功！！')