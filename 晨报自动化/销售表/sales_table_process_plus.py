import pandas as pd
import numpy as np

pd.set_option('display.width',120)
pd.set_option('display.max_columns', 50)
pd.set_option('precision',3)

# 导入并处理 各个原始数据表
def table_merge(month): 
    # 导入 电视购物_TV表
    TV_df = pd.read_excel('./原始表/电视购物_TV.xls',sheet_name='sheet1',header=15,usecols=[4,5,7,9,10,12,13,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    TV_df = TV_df.iloc[0:-1]
    TV_df = TV_df.fillna(method='ffill')
    TV_df['公司'] = '电视购物公司'
    TV_df['年月'] = month
    TV_df['渠道1'] = 'TV'
    TV_df['渠道2'] = 'TV'
    print(TV_df.shape)
    # 导入 电视购物_INT表
    INT_df = pd.read_excel('./原始表/电视购物_INT.xls',sheet_name='sheet1',header=15,usecols=[4,5,7,9,10,12,13,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    INT_df = INT_df.iloc[0:-1]
    INT_df = INT_df.fillna(method='ffill')
    INT_df['公司'] = '电视购物公司'
    INT_df['年月'] = month
    INT_df['渠道1'] = 'INT'
    INT_df['渠道2'] = '新媒体'
    print(INT_df.shape)
    # 导入 电视购物_CTL表
    CTL_df = pd.read_excel('./原始表/电视购物_CTL.xls',sheet_name='sheet1',header=15,usecols=[4,5,7,9,10,12,13,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    CTL_df = CTL_df.iloc[0:-1]
    CTL_df = CTL_df.fillna(method='ffill')
    CTL_df['公司'] = '电视购物公司'
    CTL_df['年月'] = month
    CTL_df['渠道1'] = 'CTL'
    CTL_df['渠道2'] = 'CTL'
    print(CTL_df.shape)
    # 导入 电视购物_其他表
    OT_df = pd.read_excel('./原始表/电视购物_其它.xls',sheet_name='sheet1',header=15,usecols=[4,5,7,9,10,12,13,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    OT_df = OT_df.iloc[0:-1]
    OT_df = OT_df.fillna(method='ffill')
    OT_df['公司'] = '电视购物公司'
    OT_df['年月'] = month
    OT_df['渠道1'] = 'TV'
    OT_df['渠道2'] = '其他'
    print(OT_df.shape)
    # 导入 旅行社_TV表
    TR_TV_df = pd.read_excel('./原始表/旅行社_TV.xls',sheet_name='sheet1',header=15,usecols=[4,5,7,9,10,12,13,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    TR_TV_df = TR_TV_df.iloc[0:-1]
    TR_TV_df = TR_TV_df.fillna(method='ffill')
    TR_TV_df['公司'] = '旅行社'
    TR_TV_df['年月'] = month
    TR_TV_df['渠道1'] = '旅行社'
    TR_TV_df['渠道2'] = 'TV'
    print(TR_TV_df.shape)
    # 导入 旅行社_INT表
    TR_INT_df = pd.read_excel('./原始表/旅行社_INT.xls',sheet_name='sheet1',header=15,usecols=[4,5,7,9,10,12,13,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    TR_INT_df = TR_INT_df.iloc[0:-1]
    TR_INT_df = TR_INT_df.fillna(method='ffill')
    TR_INT_df['公司'] = u'旅行社'
    TR_INT_df['年月'] = month
    TR_INT_df['渠道1'] = '旅行社'
    TR_INT_df['渠道2'] = '新媒体'
    print(TR_INT_df.shape)
    # 导入 旅行社_CTL表
    TR_CTL_df = pd.read_excel('./原始表/旅行社_CTL.xls',sheet_name='sheet1',header=15,usecols=[4,5,7,9,10,12,13,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    TR_CTL_df = TR_CTL_df.iloc[0:-1]
    TR_CTL_df = TR_CTL_df.fillna(method='ffill')
    TR_CTL_df['公司'] = '旅行社'
    TR_CTL_df['年月'] = month
    TR_CTL_df['渠道1'] = '旅行社'
    TR_CTL_df['渠道2'] = 'CTL'
    print(TR_CTL_df.shape)
    # 导入 贸易公司_全部表
    MAOYI_df = pd.read_excel('./原始表/贸易公司_ALL.xls',sheet_name='sheet1',header=15,usecols=[4,5,7,9,10,12,13,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    MAOYI_df = MAOYI_df.iloc[0:-1]
    MAOYI_df= MAOYI_df.fillna(method='ffill')
    MAOYI_df['公司'] = '全球购-东方购物贸易'
    MAOYI_df['年月'] = month
    MAOYI_df['渠道1'] = '全球购'
    MAOYI_df['渠道2'] = '新媒体'
    print(MAOYI_df.shape)
    # 合并所有表格
    ALL_merge_df = pd.concat([TV_df,INT_df,CTL_df,OT_df,TR_TV_df,TR_INT_df,TR_CTL_df,MAOYI_df])
    print(ALL_merge_df.shape)
    # 导出为表格
    ALL_merge_df['商品编号'] = ALL_merge_df['商品编号'].astype(str)
    ALL_merge_df['商品编号'] = ALL_merge_df['商品编号'].str.split('.').str[0]
    ALL_merge_df['供应商编号'] = ALL_merge_df['供应商编号'].astype(str)
    ALL_merge_df['供应商编号'] = ALL_merge_df['供应商编号'].str.split('.').str[0]
    ALL_merge_df['品牌编号'] = ALL_merge_df['品牌编号'].astype(str)
    ALL_merge_df['品牌编号'] = ALL_merge_df['品牌编号'].str.split('.').str[0]
    ALL_merge_df.rename(columns={'商品名称.1':'商品名称'},inplace=True)
    ALL_merge_df.to_excel('./ALL_merge_table.xlsx', sheet_name='table', index=False, encoding='utf-8')
    print('所有 表格合并、处理完成！!')
    return ALL_merge_df

def func_product(x):
    if 'I' in str(x):
        return 'IC商品'
    else:
        return 'TV商品'
    
def func_TVP(x):
    if 'TVP' in str(x):
        return '是'
    elif 'ICP' in str(x):
        return '是'
    else:
        return ''
    
def join_str(x):
    return ''.join(x)

def table_process(df):
    df['商品区分'] = df['MD号码'].apply(func_product)
    df['主供应商'] = df['供应商名称'].str.replace(r'\(.*?\)','')
    df['主供应商'] = df['供应商名称'].str.replace(r'\（.*?\）','')
    df['主供应商'] = df['供应商名称'].str.findall('[\u4e00-\u9fa5]')
    df['主供应商'] = df['主供应商'].apply(join_str)
    df['是否TVP'] = df['供应商名称'].apply(func_TVP)
    
    cols = [33,32,34,0,1,36,2,3,4,7,8,9,5,6,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,35,37,38]
    df=df.iloc[:,cols]
    
    print(df.info())
    df.to_excel('./销售处理表.xlsx', sheet_name='table', index=False, encoding='utf-8')
    print('销售表 初步处理完成！！')
    return df

if __name__ == '__main__':

    month = '202103'
    df = table_merge(month)
    df_final = table_process(df)
    
