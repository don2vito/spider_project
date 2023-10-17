import akshare as ak
import pandas as pd
import json
import requests
import chardet
import time


def zhengzhou(date):
    # czce_warehouse_receipt_df = ak.futures_czce_warehouse_receipt(trade_date=date)
    # print(czce_warehouse_receipt_df)
    # df = pd.DataFrame.from_dict(czce_warehouse_receipt_df, orient='index').T
    # print(df)
    # df.to_excel('zhengzhou.xlsx')
    headers={
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
              'Host': 'www.czce.com.cn',
              'Referer': 'http://www.czce.com.cn/'
              }
    url = 'http://www.czce.com.cn/cn/DFSStaticFiles/Future/'+date[0:4]+'/'+date+'/FutureDataWhsheet.htm'
    res = requests.get(url,headers=headers)
    res.encoding = chardet.detect(res.content)['encoding']
    res = res.text
    df = pd.read_html(res)[0]
    df.to_excel('zhengzhou.xlsx')
    
    
def dalian(date):
    url = 'http://www.dce.com.cn/publicweb/quotesdata/wbillWeeklyQuotes.html?wbillWeeklyQuotes.variety=all&year='+date[0:4]+'&month='+str(int(date[4:6])-1)+'&day='+date[6:]
    res = requests.get(url).text
    df = pd.read_html(res)[0]
    # futures_dce_warehouse_receipt_df = ak.futures_dce_warehouse_receipt(trade_date="20200702")
    # print(futures_dce_warehouse_receipt_df)
    # df = pd.DataFrame.from_dict(futures_dce_warehouse_receipt_df, orient='index').T
    # print(df)
    df.to_excel('dalian.xlsx')
    
    
def shanghai(date):
    # futures_shfe_warehouse_receipt_df = ak.futures_shfe_warehouse_receipt(trade_date=date)
    # print(futures_shfe_warehouse_receipt_df)
    # df = pd.DataFrame.from_dict(futures_shfe_warehouse_receipt_df, orient='index').T
    # print(df)
    # df.to_excel('shanghai.xlsx')
    url = 'https://www.shfe.com.cn/data/dailydata/'+date+'dailystock.dat'
    res = requests.get(url).text
    json_data=json.loads(res)
    datas_cangdan = []
    results_cangdan = json_data['o_cursor']
    for cangdan in results_cangdan:
        data_cangdan = {
            '日期': date,
            '交易所': 'SQH',
            '地区': cangdan['REGNAME'].strip(),
            '仓库': cangdan['WHABBRNAME'],
            '期货': cangdan['WRTWGHTS'],
            '增减': cangdan['WRTCHANGE']
        }
        datas_cangdan.append(data_cangdan)
    df = pd.DataFrame(datas_cangdan)
    df.to_excel('shanghai.xlsx')

    
if __name__ == '__main__':
    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d')
    zhengzhou(date)
    dalian(date)
    shanghai(date)