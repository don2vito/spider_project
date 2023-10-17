import akshare as ak
import pandas as pd
import datetime
import json
import os
import schedule
import time
from alive_progress import alive_bar
import PySimpleGUI as sg

"""
改进：
1. 使用 pipenv 建立虚拟环境
2. 使用 PySimpleGUI 打包 exe 文件，显示图形化交互界面
"""

def zhengzhou(date):
    df_temp = pd.DataFrame({'state': ['占位'],'date': [date]})
    with pd.ExcelWriter(f'./{date}/zhengzhou-{date}.xlsx',mode='w',engine='openpyxl') as writer:
        df_temp.to_excel(writer,sheet_name=date, index=False)
    df_dict = ak.futures_czce_warehouse_receipt(trade_date=date)
    for k,v in zip(df_dict.keys(),df_dict.values()):
        df = pd.DataFrame(v)
        df['品种'] = k
        df = df.apply(pd.to_numeric,errors='ignore')
        with pd.ExcelWriter(f'./{date}/zhengzhou-{date}.xlsx',mode='a',engine='openpyxl',if_sheet_exists='new') as writer:
            df.to_excel(writer, sheet_name=k, index=False)

def dalian(date):
    df_dict = ak.futures_dce_warehouse_receipt(trade_date=date)
    df1 = pd.DataFrame()
    for k, v in zip(df_dict.keys(), df_dict.values()):
        df2 = pd.DataFrame(v)
        df2['品种0'] = k
        df1 = pd.concat([df1, df2])
    df1 = df1.apply(pd.to_numeric,errors='ignore')
    df1.to_excel(f'./{date}/dalian-{date}.xlsx', index=False,sheet_name=date)

def shanghai(date):
    df_dict = ak.futures_shfe_warehouse_receipt(trade_date=date)
    df1 = pd.DataFrame()
    for k, v in zip(df_dict.keys(), df_dict.values()):
        df2 = pd.DataFrame(v)
        df1 = pd.concat([df1, df2])
    df1 = df1.apply(pd.to_numeric,errors='ignore')
    df1.to_excel(f'./{date}/shanghai-{date}.xlsx', index=False,sheet_name=date)

def main(begin_str,end_str):
    # begin_str = str(input('请输入起始年月日（yyyymmdd）：')).strip()
    # end_str = str(input('请输入结束年月日（yyyymmdd）：')).strip()
    begin_year,begin_month,begin_day = int(begin_str[0:4]),int(begin_str[4:6]),int(begin_str[6:8])
    end_year,end_month,end_day = int(end_str[0:4]),int(end_str[4:6]),int(end_str[6:8])
    begin = datetime.date(begin_year,begin_month,begin_day)
    end = datetime.date(end_year,end_month,end_day)
    with alive_bar((end - begin).days+1) as bar:
        for i in range((end - begin).days+1):
            bar()
            day = begin + datetime.timedelta(days=i)
            date = day.strftime('%Y%m%d')
            
            filepath = './' + date
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            
            try:
                zhengzhou(date)
            except ValueError:
                pass
            try:
                dalian(date)
            except json.JSONDecodeError:
                pass
            try:
                shanghai(date)
            except json.JSONDecodeError:
                pass
            print(f'{date} 仓单数据获取完成……')
    print(f'本次仓单数据全部获取完成!!')

def gui():
    sg.change_look_and_feel('Material1')
    layout = [
             [sg.Text('请输入起始年月日（yyyymmdd）:',font=("微软雅黑", 10)),sg.InputText(font=("微软雅黑", 10))],
             [sg.Text('请输入结束年月日（yyyymmdd）:',font=("微软雅黑", 10)),sg.InputText(font=("微软雅黑", 10))],          
             # [sg.Text('任务完成进度',font=("微软雅黑", 10))],
             # [sg.ProgressBar(100, orientation='h', size=(77, 20),key='progressbar')],
             [sg.Button('确定',font=("微软雅黑", 10)),sg.Button("取消",font=("微软雅黑", 10))]
             ]    
  
    window = sg.Window('期货仓单数据获取工具', layout,font=("宋体", 15),default_element_size=(50,1))  
  
    while True:
        event,values = window.read()
        if event == None:
            break
        if event == sg.WIN_CLOSED:  # 一定要写这一个语句，否则点 x 关闭窗口也会继续消耗内存
            break
        if event == '确定':
            main(str(values[0]).strip(),str(values[1]).strip())
        if event == '取消':
            break
  
    window.close()     
    

if __name__ == '__main__':
    gui()
