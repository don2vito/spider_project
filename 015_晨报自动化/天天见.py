# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 17:31:44 2021

@author: 2000102146
"""

from datetime import datetime
import pandas as pd
import xlwings as xw

df1=pd.read_excel('D:/工作/【每日工作】/日报模板/效率表/月公司销售.xls',header=4)
df2=pd.read_excel('D:/工作/【每日工作】/日报模板/效率表/月公司利润.xls',header=4)
df3=pd.read_excel('D:/工作/【每日工作】/日报模板/效率表/公司销售.xls',header=4)
df4=pd.read_excel('D:/工作/【每日工作】/日报模板/效率表/公司利润.xls',header=4)


df1=df1.iloc[:, 1:]
df2=df2.iloc[:, 1:]
df_m=pd.concat([df1,df2],axis=1,join='outer')

df3=df3.iloc[:, 1:]
df4=df4.iloc[:, 1:]
df_d=pd.concat([df3,df4],axis=1,join='outer')

print(df_m['销售金额'][3])
print(df_m['销售利润'][3])
print(df_d['销售金额'][3])
print(df_d['销售利润'][3])

print('当日的销售额是{}, 利润额是{}； 月累计销售额是{}，利润额是{}'.format(df_d['销售金额'][3], df_d['销售利润'][3], df_m['销售金额'][3], df_m['销售利润'][3]))


app = xw.App(visible=False, add_book=False)
workbook = app.books.open('D:/工作/【每日工作】/日报模板/日目标跟进.xlsx')
sh = workbook.sheets['天天见']

sh.range('D4').value = df_d['销售金额'][3]  
sh.range('D8').value = df_d['销售利润'][3]  
sh.range('F4').value = df_m['销售金额'][3]  
sh.range('F8').value = df_m['销售利润'][3]  
sh.range('F12').value = (datetime.now()).day - 1 

#today = datetime.now()
#datetime.datetime.now().day
#
#today=datetime.date.today() 
#oneday=datetime.timedelta(days=1) 
#yesterday=today-oneday
#day_y = datetime.datetime.yesterday().day
#print(today.day-1)

workbook.save()
workbook.close()
app.quit()