import akshare as ak
import pandas as pd

def zhengzhou(date):
    df_dict = ak.futures_czce_warehouse_receipt(trade_date=date)
    for k,v in zip(df_dict.keys(),df_dict.values()):
        df = pd.DataFrame(v)
        df['品种'] = k
        with pd.ExcelWriter('./zhengzhou2.xlsx',mode='a',engine='openpyxl',if_sheet_exists='new') as writer:
            df.to_excel(writer, sheet_name=k, index=False)

def dalian(date):
    df_dict = ak.futures_dce_warehouse_receipt(trade_date=date)
    df1 = pd.DataFrame()
    for k, v in zip(df_dict.keys(), df_dict.values()):
        df2 = pd.DataFrame(v)
        df2['品种0'] = k
        df1 = pd.concat([df1, df2])
    df1.to_excel('./dalian2.xlsx', index=False)

def shanghai(date):
    df_dict = ak.futures_shfe_warehouse_receipt(trade_date=date)
    df1 = pd.DataFrame()
    for k, v in zip(df_dict.keys(), df_dict.values()):
        df2 = pd.DataFrame(v)
        df1 = pd.concat([df1, df2])
    df1.to_excel('./shanghai2.xlsx', index=False)


if __name__ == '__main__':
    # now = datetime.datetime.now()
    # date = now.strftime('%Y%m%d')
    date = '20221202'
    zhengzhou(date)
    dalian(date)
    shanghai(date)