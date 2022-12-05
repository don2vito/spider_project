import akshare as ak
import pandas as pd
import datetime
import json
import os
import schedule
import time

"""
改进：
1. 可输入日期范围，循环运行(方法一)
2. 每日定时自动运行(方法二)
3. 对非营业日进行跳过
4. 默认对输出表格中的数字进行数值化
"""

def zhengzhou(date):
    df_temp = pd.DataFrame({'state': ['0', '1'],'num': [0, 1]})
    with pd.ExcelWriter(f'./{date}/zhengzhou-{date}.xlsx',mode='w',engine='openpyxl') as writer:
        df_temp.to_excel(writer, sheet_name='占位', index=False)
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
    df1.to_excel(f'./{date}/dalian-{date}.xlsx', index=False)

def shanghai(date):
    df_dict = ak.futures_shfe_warehouse_receipt(trade_date=date)
    df1 = pd.DataFrame()
    for k, v in zip(df_dict.keys(), df_dict.values()):
        df2 = pd.DataFrame(v)
        df1 = pd.concat([df1, df2])
    df1 = df1.apply(pd.to_numeric,errors='ignore')
    df1.to_excel(f'./{date}/shanghai-{date}.xlsx', index=False)

def main1():
    begin_str = str(input('请输入起始年月日（yyyymmdd）：')).strip()
    end_str = str(input('请输入结束年月日（yyyymmdd）：')).strip()
    begin_year,begin_month,begin_day = int(begin_str[0:4]),int(begin_str[4:6]),int(begin_str[6:8])
    end_year,end_month,end_day = int(end_str[0:4]),int(end_str[4:6]),int(end_str[6:8])
    begin = datetime.date(begin_year,begin_month,begin_day)
    end = datetime.date(end_year,end_month,end_day)
    for i in range((end - begin).days+1):
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
        
def main2():
    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d')
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
    

if __name__ == '__main__':
    def job():
        main2()
        print('我正在运行……')
    
    schedule.every().day.at('16:30').do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
