import pandas as pd
import numpy as np
import os
import re
import requests
import json
import datetime
from xml.etree import ElementTree
import xmltodict
import sqlite3
import time
import warnings
warnings.filterwarnings("ignore")

# 待处理：spider_ZJ 的字段映射处理，并且需要对齐字段!!
# 待处理：多余 print 的清理!!
# 报错：    df_DQH_process = df_DQH.loc[~df_DQH['商品名称'].str.contains('小计|总计')]
# AttributeError: 'NoneType' object has no attribute 'loc'

# 时间处理模块
def dateRange(beginDate, endDate):
    dates = []
    years = []
    months = []
    month4DQHs = []
    days = []
    dt = datetime.datetime.strptime(beginDate, "%Y%m%d")
    date = beginDate[:]
    year = beginDate[0:4]
    day = beginDate[6:8]
    month = beginDate[4:6]
    month4DQH = str(int(beginDate[4:6]) - 1)
    while date <= endDate:
        dates.append(date)
        years.append(year)
        days.append(day)
        months.append(month)
        month4DQHs.append(month4DQH)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y%m%d")
        year = dt.strftime("%Y%m%d")[0:4]
        day = dt.strftime("%Y%m%d")[6:8]
        month = dt.strftime("%Y%m%d")[4:6]
        month4DQH = str(int(dt.strftime("%Y%m%d")[4:6]) - 1)
    # print(dates)
    return dates,years,months,month4DQHs,days

# 文本转日期模块
def str2date(begin_str,end_str):
    beginDate = datetime.datetime.strptime(begin_str, '%Y%m%d').strftime('%Y%m%d')
    endDate = datetime.datetime.strptime(end_str , '%Y%m%d').strftime('%Y%m%d')
    return beginDate, endDate

# 时间（文本）处理模块 ——> 改用新的时间处理模块，此函数废弃
def date(year,month,day):
    if len(month) == 1:
        month_after = '0' + month
    else:
        month_after = month
    return year + month_after + day

# 文件夹生成模块
def create_folder(result_path):
    if not os.path.exists(result_path):
        os.makedirs(result_path)

# 中金所数据爬虫模块
def spider_ZJ(year_str,month_str,day_str,date_str):
    result = []
    file_url = 'http://www.cffex.com.cn/sj/hqsj/rtj/' + year_str + month_str + '/' + day_str + '/index.xml'
    try:
        respose_str = requests.get(file_url,headers=headers).text
        xml_text = str(respose_str)

        with open('./html2xml.xml','w') as fp:
            fp.write(xml_text)
        # print('写入XML文件 成功！')

        root = ElementTree.parse('./html2xml.xml')
        xml_data = root.getroot()
        xml_str = ElementTree.tostring(xml_data,method='xml')
        data_dict = dict(xmltodict.parse(xml_str))
        with open('./xml2json.json','w+') as json_file:
            json.dump(data_dict,json_file,indent=4,sort_keys=True)
        # print('写入JSON文件 成功！')

        with open('./xml2json.json', 'r') as f:
            json_data = json.load(f)
        datas = []
        results = json_data['dailydatas']['dailydata']
        for data in results:
            data['日期'] = date_str
            data['交易所'] = 'ZJ'
            datas.append(data)
        result = result.append(pd.DataFrame(datas))
        result = result.rename(columns={
                                        'sum持仓量': '持仓量',
                                        'sum沉淀资金': '沉淀资金',
                                        '日期_heyue_pivot': '日期',
                                        '交易所_heyue_pivot': '交易所'
                                        }
                                )
        result = result[['']]
    except:
        pass
    return result

# 大连交易所数据爬虫模块
def spider_DQH(year_str,month_str4DQH,day_str,date_str):
    result = []
    url = 'http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html?dayQuotes.variety=all&dayQuotes.trade_type=0&year=' + year_str + '&month=' + month_str4DQH + '&day=' + day_str
    try:
        # res = requests.post(url,json_data).text
        res = requests.get(url).text
        # print(res)
        df = pd.read_html(res)[0]
        df['日期'] = date_str
        df['交易所'] = 'DQH'
    except:
        pass
    result = result.append(df)

# 郑州交易所数据爬虫模块
def spider_ZQH(year_str, date_str):
    result = []
    url = 'http://www.czce.com.cn/cn/DFSStaticFiles/Future/' + year_str + '/' + date_str + '/FutureDataDaily.htm'
    try:
        df = pd.read_html(url)[0]
        df = df[0:-1]
        df['日期'] = date_str
        df['交易所'] = 'ZQH'
        # print(df.info())
    except:
        pass
    result = result.append(df)


# 大连交易所数据处理模块
def DQH_process(date_str,DQH_spider_df):
    df_DQH = DQH_spider_df
    df_DQH_process = df_DQH.loc[~df_DQH['商品名称'].str.contains('小计|总计')]
    df_DQH_process['成交量'] = df_DQH_process['成交量'].str.replace(',', '').astype('int')
    df_DQH_process['持仓量'] = df_DQH_process['持仓量'].str.replace(',', '').astype('int')
    df_DQH_process['成交额'] = df_DQH_process['成交额'].str.replace(',', '').astype('float')
    # 要把万元转换成元
    df_DQH_process['成交额'] = df_DQH_process['成交额'].apply(lambda x: x * 10000)
    df_DQH_process['收盘价'] = df_DQH_process['收盘价'].str.replace(',', '').astype('float')
    df_DQH_process['日期'] = date_str
    df_DQH_process['交易所'] = 'DQH'
    df_DQH_process = df_DQH_process[['日期','交易所','商品名称','成交量','持仓量','成交额','收盘价',]]
    df_param = param_table_process()
    df_DQH_merge = pd.merge(df_DQH_process,df_param,left_on='商品名称',right_on='品种',how='left',suffixes=('_DQH','_merge'))
    df_DQH_merge['沉淀资金'] = df_DQH_merge['收盘价'] * df_DQH_merge['持仓量'] * df_DQH_merge['合约乘数']
    df_DQH_merge = df_DQH_merge.rename(columns={'交易所_DQH': '交易所'})
    df_DQH_process = df_DQH_merge[['日期', '交易所', '商品名称','代码', '成交量', '持仓量', '成交额', '沉淀资金']]
    # 合约表透视汇总
    df_DQH_pivot = pd.pivot_table(df_DQH_process,index=['日期','交易所','商品名称','代码',],values=['成交量', '持仓量','成交额', '沉淀资金'],aggfunc=[np.sum]).reset_index()
    # 将透视表多层表头转换为一层
    df_DQH_pivot_copy = df_DQH_pivot.copy(deep=True)
    col = []
    for i in df_DQH_pivot_copy.columns:
        i = list(i)
        i[1] = str(i[1])
        col.append(''.join(i))
    df_DQH_pivot_copy.columns = col
    df_DQH_pivot_copy.reset_index()  
    # 关联汇总表和参数表字段，得到所需字段
    df_DQH_pivot_copy = df_DQH_pivot_copy.rename(columns={'sum持仓量': '持仓量','sum沉淀资金': '沉淀资金','sum成交量':'成交量','sum成交额':'成交额'})
    df_DQH_process = df_DQH_pivot_copy
    print('大连交易所数据 处理完成！')
    return df_DQH_process

# 中金所数据处理模块
def ZJ_process(date_str,ZJ_spider_df):
    df_ZJ = ZJ_spider_df
    df_ZJ_process = df_ZJ.loc[~df_ZJ['合约代码'].str.contains('小计|合计')]
    df_ZJ_process['商品名称'] = df_ZJ_process['合约代码'].map(lambda x:x.split('-')[0])
    # 商品名称字母，利用正则表达式
    df_ZJ_process['商品名称'] = df_ZJ_process['商品名称'].map(lambda x:re.findall('[A-Z]+',x)[0])
    df_ZJ_process['成交额'] = df_ZJ_process['成交金额']
    # 要把万元转换成元
    df_ZJ_process['成交额'] = df_ZJ_process['成交额'].apply(lambda x: x * 10000)
    df_ZJ_process['收盘价'] = df_ZJ_process['今收盘']
    df_ZJ_process['日期'] = date_str
    df_ZJ_process['交易所'] = 'ZJ'
    df_ZJ_process = df_ZJ_process[['日期','交易所','商品名称','成交量','持仓量','成交额','收盘价',]]
    # print(df_ZJ_process.tail(20))
    # print(df_ZJ_process.info())
    df_param = param_table_process()
    df_ZJ_merge = pd.merge(df_ZJ_process,df_param,left_on='商品名称',right_on='代码',how='left',suffixes=('_ZJ','_merge'))
    df_ZJ_merge['沉淀资金'] = df_ZJ_merge['收盘价'] * df_ZJ_merge['持仓量'] * df_ZJ_merge['合约乘数']
    df_ZJ_merge = df_ZJ_merge.rename(columns={'商品名称': '商品名称x'})
    df_ZJ_merge = df_ZJ_merge.rename(columns={'交易所_ZJ': '交易所','品种':'商品名称'})
    df_ZJ_process = df_ZJ_merge[['日期', '交易所', '商品名称','代码', '成交量', '持仓量', '成交额', '沉淀资金']]
    # 合约表透视汇总
    df_ZJ_pivot = pd.pivot_table(df_ZJ_process,index=['日期','交易所','商品名称','代码',],values=['成交量', '持仓量','成交额', '沉淀资金'],aggfunc=[np.sum]).reset_index()
    # 将透视表多层表头转换为一层
    df_ZJ_pivot_copy = df_ZJ_pivot.copy(deep=True)
    col = []
    for i in df_ZJ_pivot_copy.columns:
        i = list(i)
        i[1] = str(i[1])
        col.append(''.join(i))
    df_ZJ_pivot_copy.columns = col
    df_ZJ_pivot_copy.reset_index()  
    # 关联汇总表和参数表字段，得到所需字段
    df_ZJ_pivot_copy = df_ZJ_pivot_copy.rename(columns={'sum持仓量': '持仓量','sum沉淀资金': '沉淀资金','sum成交量':'成交量','sum成交额':'成交额'})
    df_ZJ_process = df_ZJ_pivot_copy
    print('中金所数据 处理完成！')
    return df_ZJ_process

# 郑州交易所数据处理模块
def ZQH_process(date_str,ZQH_spider_df):
    df_ZQH = ZQH_spider_df
    df_ZQH_process = df_ZQH.loc[~df_ZQH['品种月份'].str.contains('小计|总计')]
    # 商品名称字母，利用正则表达式
    df_ZQH_process['商品名称'] = df_ZQH_process['品种月份'].map(lambda x:re.findall('[A-Z]+',x)[0])
    df_ZQH_process['成交量'] = df_ZQH_process['成交量(手)'].str.replace(',', '').astype('int')
    df_ZQH_process['持仓量'] = df_ZQH_process['持仓量'].str.replace(',', '').astype('int')
    # 要把万元转化为元
    df_ZQH_process['成交额'] = df_ZQH_process['成交额(万元)'].str.replace(',', '').astype('float')
    df_ZQH_process['成交额'] = df_ZQH_process['成交额'].apply(lambda x:x*10000)
    df_ZQH_process['收盘价'] = df_ZQH_process['今收盘'].str.replace(',', '').astype('float')
    df_ZQH_process['日期'] = date_str
    df_ZQH_process['交易所'] = 'ZQH'
    df_ZQH_process = df_ZQH_process[['日期','交易所','商品名称','成交量','持仓量','成交额','收盘价',]]
    df_param = param_table_process()
    df_ZQH_merge = pd.merge(df_ZQH_process,df_param,left_on='商品名称',right_on='代码',how='left',suffixes=('_ZQH','_merge'))
    df_ZQH_merge['沉淀资金'] = df_ZQH_merge['收盘价'] * df_ZQH_merge['持仓量'] * df_ZQH_merge['合约乘数']
    df_ZQH_merge = df_ZQH_merge.rename(columns={'商品名称': '商品名称x'})
    df_ZQH_merge = df_ZQH_merge.rename(columns={'交易所_ZQH': '交易所','品种':'商品名称'})
    df_ZQH_process = df_ZQH_merge[['日期', '交易所', '商品名称','代码', '成交量', '持仓量', '成交额', '沉淀资金']]
    # 合约表透视汇总
    df_ZQH_pivot = pd.pivot_table(df_ZQH_process,index=['日期','交易所','商品名称','代码',],values=['成交量', '持仓量','成交额', '沉淀资金'],aggfunc=[np.sum]).reset_index()
    # 将透视表多层表头转换为一层
    df_ZQH_pivot_copy = df_ZQH_pivot.copy(deep=True)
    col = []
    for i in df_ZQH_pivot_copy.columns:
        i = list(i)
        i[1] = str(i[1])
        col.append(''.join(i))
    df_ZQH_pivot_copy.columns = col
    df_ZQH_pivot_copy.reset_index()  
    # 关联汇总表和参数表字段，得到所需字段
    df_ZQH_pivot_copy = df_ZQH_pivot_copy.rename(columns={'sum持仓量': '持仓量','sum沉淀资金': '沉淀资金','sum成交量':'成交量','sum成交额':'成交额'})
    df_ZQH_process = df_ZQH_pivot_copy
    print('郑州交易所 处理完成！')
    return df_ZQH_process

# 上海交易所数据爬虫模块
def spider_SQH(date_str):
    res = requests.get('http://www.shfe.com.cn/data/dailydata/kx/kx' + date_str + '.dat')
    json_data=json.loads(res.text)
    datas_heyue = []
    results_heyue = json_data['o_curinstrument']
    datas_huizong= []
    results_huizong = json_data['o_curproduct']

    for heyue in results_heyue:
        data_heyue = {
            '日期': date_str,
            '交易所': 'SQH',
            '商品名称': heyue['PRODUCTNAME'].strip(),
            '正常成交量': heyue['VOLUME'],
            'TAS成交量': heyue['TASVOLUME'],
            '持仓量': heyue['OPENINTEREST'],
            '收盘价': heyue['CLOSEPRICE'],
            '备注':heyue['DELIVERYMONTH'].strip()
        }
        datas_heyue.append(data_heyue)
    df_heyue = pd.DataFrame(datas_heyue)
    # 剔除“商品名称”中为总计和原油TAS的行，“备注”中为小计的行
    df_heyue = df_heyue.loc[~df_heyue['商品名称'].str.contains('总计|原油TAS')]
    df_heyue = df_heyue.loc[~df_heyue['备注'].str.contains('小计')]
    df_heyue['成交量'] = df_heyue['正常成交量'].astype('int')
    df_heyue['持仓量'] = df_heyue['持仓量'].astype('int')
    df_heyue['收盘价'] = df_heyue['收盘价'].astype('float')
    df_heyue = df_heyue[['日期','交易所','商品名称','成交量','持仓量','收盘价','备注']]
    print('上期所合约数据 爬取完成！')

    for huizong in results_huizong:
        data_huizong = {
            '日期': date_str,
            '交易所': 'SQH',
            '商品名称': huizong['PRODUCTNAME'].strip(),
            '成交量': huizong['VOLUME'],
            '成交额': huizong['TURNOVER'],
        }
        datas_huizong.append(data_huizong)
    df_huizong = pd.DataFrame(datas_huizong)
    # 剔除“商品名称”中为总计的行
    df_huizong = df_huizong.loc[~df_huizong['商品名称'].str.contains('总计')]
    # 将成交额的单位“亿元”转换成“元”
    df_huizong['成交额'] = df_huizong['成交额'].apply(lambda x: x * 100000000)
    df_huizong['成交量'] = df_huizong['成交量'].astype('int')
    df_huizong = df_huizong[['日期','交易所','商品名称','成交量','成交额']]
    print('上期所汇总数据 爬取完成！')
    return df_heyue,df_huizong

# 上海交易所数据处理模块
def SQH_process(df_heyue,df_huizong):
    df_param = param_table_process()
    df_SQH_heyue_merge = pd.merge(df_heyue,df_param,left_on='商品名称',right_on='品种',how='left',suffixes=('_SQH_heyue','_merge'))
    df_SQH_heyue_merge['沉淀资金'] = df_SQH_heyue_merge['收盘价'] * df_SQH_heyue_merge['持仓量'] * df_SQH_heyue_merge['合约乘数']
    df_SQH_heyue_merge = df_SQH_heyue_merge.rename(columns={'交易所_SQH_heyue': '交易所'})
    df_SQH_heyue_merge = df_SQH_heyue_merge[['日期', '交易所', '商品名称','代码', '成交量', '持仓量', '收盘价', '合约乘数','沉淀资金']]
    # 合约表透视汇总
    df_heyue_pivot = pd.pivot_table(df_SQH_heyue_merge,index=['日期','交易所','商品名称','代码',],values=['成交量', '持仓量','沉淀资金'],aggfunc=[np.sum]).reset_index()
    # 将透视表多层表头转换为一层
    df_heyue_pivot_copy = df_heyue_pivot.copy(deep=True)
    col = []
    for i in df_heyue_pivot_copy.columns:
        i = list(i)
        i[1] = str(i[1])
        col.append(''.join(i))
    df_heyue_pivot_copy.columns = col
    df_heyue_pivot_copy.reset_index()  
    # 关联汇总表和参数表字段，得到所需字段
    df_merge = pd.merge(df_heyue_pivot_copy,df_huizong,left_on='商品名称',right_on='商品名称',how='left',suffixes=('_heyue_pivot','_huizong'))
    df_merge = df_merge.rename(columns={'sum持仓量': '持仓量','sum沉淀资金': '沉淀资金','日期_heyue_pivot':'日期','交易所_heyue_pivot':'交易所'})
    df_SQH_process = df_merge[['日期', '交易所', '商品名称','代码', '成交量', '持仓量', '成交额', '沉淀资金']]
    print('上海交易所数据 处理完成！')
    return df_SQH_process

# 参数表读取模块
def param_table_process():
    df_param = pd.read_excel('./参数表.xlsx' )
    return df_param

# 汇总数据处理模块
def dataframes_porcess(result_path,df_SQH_process,df_DQH_process,df_ZQH_process,df_ZJ_process,df_param):
    # 追加合并数据，透视数据
    df_final = pd.concat([df_SQH_process,df_DQH_process,df_ZQH_process,df_ZJ_process])
    # 把元转换成万元
    df_final['成交额（万元）'] = df_final['成交额'].apply(lambda x:round(x/10000,2))
    df_final['沉淀资金（万元）'] = df_final['沉淀资金'].apply(lambda x:round(x/10000,2))
    df_final = df_final[['日期', '交易所', '商品名称','代码', '成交量', '持仓量','成交额（万元）','沉淀资金（万元）']]
    # 关联结果
    df_final_merge = pd.merge(df_final,df_param,left_on='代码',right_on='代码',how='left',suffixes=('_final_merge','_param'))
    df_final_merge = df_final_merge.rename(columns={'代码_final_merge': '代码','品种_final_merge': '品种','交易所_final_merge': '交易所',})
    df_final_merge = df_final_merge[['日期', '交易所', '商品名称','代码', '成交量', '持仓量','成交额（万元）','沉淀资金（万元）','保证金','停板幅度','合约乘数','最小变动','夜盘']]
    # 透视结果
    # 直接逆透视专为一维化
    df_final_pivot = pd.melt(df_final, id_vars=['日期', '交易所', '商品名称','代码'], value_vars=list(df_final.columns[4:]), var_name='统计指标', value_name='统计值')
    # 使用 openpyxl 保存在一个workbook，并设置格式
    file_path_str = date(year, month, day) + '_daily_result.xlsx'
    writer = pd.ExcelWriter(os.path.join(result_path,file_path_str))
    df_final_merge.to_excel(writer,'merge',index=False)
    df_final_pivot.to_excel(writer,'pivot',index=False)
    writer.save()
    print('保存结果文件 成功！')
    return df_final_merge,df_final_pivot

# 数据入库模块
def add2db(date_str,df_final_merge, df_final_pivot):
    conn = sqlite3.connect("luwenliang.db")
    df_final_merge.to_sql('merge', con=conn,if_exists='append')
    df_final_pivot.to_sql('pivot', con=conn,if_exists='append')
    print(f'{date_str} 添加数据至数据库 完成！')

# 主程序
def main(beginDate, endDate):
    time_begin = time.time()
    dates, years, months, month4DQHs, days = dateRange(beginDate, endDate)
    for date_str,year_str, month_str, month_str4DQH,day_str in zip(dates, years, months, month4DQHs, days):
        result_path = './' + date_str + '_' + result_file_name
        create_folder(result_path)
        # ZJ_spider_df = spider_ZJ(year_str, month_str, day_str, date_str)
        DQH_spider_df = spider_DQH(year_str, month_str4DQH, day_str, date_str)
        ZQH_spider_df = spider_ZQH(year_str, date_str)
        df_heyue,df_huizong = spider_SQH(date_str)
        df_SQH_process = SQH_process(df_heyue,df_huizong)
        df_DQH_process = DQH_process(date_str,DQH_spider_df)
        df_ZQH_process = ZQH_process(date_str,ZQH_spider_df)
        # df_ZJ_process = ZJ_process(date_str,ZJ_spider_df)
        df_param = param_table_process()
        df_final_merge, df_final_pivot = dataframes_porcess(result_path,df_SQH_process,df_DQH_process,df_ZQH_process,df_param)
        add2db(df_final_merge, df_final_pivot)
    time_end = time.time()
    print('运行共耗时 {.2f} 秒'.format(time_end - time_begin))


if __name__ == '__main__':
    begin_str = str(input('请输入起始年月日（yyyymmdd）：')).strip()
    end_str = str(input('请输入结束年月日（yyyymmdd）：')).strip()
    beginDate, endDate = str2date(begin_str, end_str)
    # 输出文件夹名可以自行定义
    result_file_name = '结果数据'
    headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
                }
    main(beginDate, endDate)