import pandas as pd
import numpy as np

pd.set_option('display.width',120)
pd.set_option('display.max_columns', 50)
pd.set_option('precision',3)

# 合并 电视购物_新媒体 表格
'''
def merge_INT_tables():
    # 导入表
    INT_df1 = pd.read_excel('./原始表/电视购物_INT_202008_1.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,49,50,52,53,55,56])
    INT_df1 = INT_df1.iloc[0:-1]
    INT_df1 = INT_df1.fillna(method='ffill')
    # print(INT_df1.isnull().sum())
    # print(INT_df1.shape)
    
    INT_df2 = pd.read_excel('./原始表/电视购物_INT_202008_2.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,49,50,52,53,55,56])
    INT_df2 = INT_df2.iloc[0:-1]
    INT_df2 = INT_df2.fillna(method='ffill')
    # print(INT_df2.isnull().sum())
    # print(INT_df2.shape)

    INT_df3 = pd.read_excel('./原始表/电视购物_INT_202008_3.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,49,50,52,53,55,56])
    INT_df3 = INT_df3.iloc[0:-1]
    INT_df3 = INT_df3.fillna(method='ffill')
    # print(INT_df3.isnull().sum())
    # print(INT_df3.shape)
    INT_df4 = pd.read_excel('./原始表/电视购物_INT_202008_4.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,49,50,52,53,55,56])
    INT_df4 = INT_df4.iloc[0:-1]
    INT_df4 = INT_df4.fillna(method='ffill')
    INT_df5 = pd.read_excel('./原始表/电视购物_INT_202008_5.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,49,50,52,53,55,56])
    INT_df5 = INT_df5.iloc[0:-1]
    INT_df5 = INT_df5.fillna(method='ffill')
    
    INT_df6 = pd.read_excel('./原始表/电视购物_INT_201912_6.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,49,50,52,53,55,56])
    INT_df6 = INT_df6.iloc[0:-1]
    INT_df6 = INT_df6.fillna(method='ffill')  
    INT_df7 = pd.read_excel('./原始表/电视购物_INT_201912_7.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,49,50,52,53,55,56])
    INT_df7 = INT_df7.iloc[0:-1]
    INT_df7 = INT_df7.fillna(method='ffill')
    
    # 合并表
    INT_merge_df = pd.concat([INT_df1,INT_df2,INT_df3,INT_df4,INT_df5])
    # print(INT_merge_df.shape)
    # print(INT_merge_df.head())
    # 透视表
    INT_groupby_df = INT_merge_df.groupby(['MD号码','MD名','大分类编号','大分类名','中分类编号','中分类名称','供应商编号','供应商名称','商品编号.1','商品名称.1','品牌编号','品牌名称']).sum()
    INT_groupby_df = INT_groupby_df.reset_index()
    # print(INT_groupby_df.shape)
    # print(INT_groupby_df.head())
    # 导出表
    INT_groupby_df.to_excel('./INT_groupby_table.xlsx', sheet_name='table', index=False, encoding='utf-8')
    print('电视购物_新媒体 表格合并完成！!')
'''

# 导入并处理 各个原始数据表
def table_process(month):
    
    
    # 导入 电视购物_TV表
    TV_df = pd.read_excel('./原始表/电视购物_TV_202104.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    TV_df = TV_df.iloc[0:-1]
    TV_df = TV_df.fillna(method='ffill')
    TV_df[u'公司'] = u'电视购物公司'
    TV_df[u'年月'] = month
    TV_df[u'渠道'] = u'TV'
    # print(TV_df.isnull().sum())
    print(TV_df.shape)
    # print(TV_df.head())
    # 导入 电视购物_INT表
    INT_df = pd.read_excel(u'./原始表/电视购物_INT_202104.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    INT_df = INT_df.iloc[0:-1]
    INT_df = INT_df.fillna(method='ffill')
    INT_df[u'公司'] = u'电视购物公司'
    INT_df[u'年月'] = month
    INT_df[u'渠道'] = '新媒体'
    # print(INT_df.isnull().sum())
    print(INT_df.shape)
    # print(INT_df.head())
    # 导入 电视购物_CTL表
    CTL_df = pd.read_excel(u'./原始表/电视购物_CTL_202104.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    CTL_df = CTL_df.iloc[0:-1]
    CTL_df = CTL_df.fillna(method='ffill')
    CTL_df[u'公司'] = u'电视购物公司'
    CTL_df[u'年月'] = month
    CTL_df[u'渠道'] = 'CTL'
    # print(CTL_df.isnull().sum())
    print(CTL_df.shape)
    # print(CTL_df.head())
    # 导入 电视购物_其他表
    OT_df = pd.read_excel(u'./原始表/电视购物_其它_202104.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    OT_df = OT_df.iloc[0:-1]
    OT_df = OT_df.fillna(method='ffill')
    OT_df[u'公司'] = u'电视购物公司'
    OT_df[u'年月'] = month
    OT_df[u'渠道'] = u'其他'
    # print(OT_df.isnull().sum())
    print(OT_df.shape)
    # print(OT_df.head())
    # 导入 旅行社_TV表
    TR_TV_df = pd.read_excel(u'./原始表/旅行社_TV_202104.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    TR_TV_df = TR_TV_df.iloc[0:-1]
    TR_TV_df = TR_TV_df.fillna(method='ffill')
    TR_TV_df[u'公司'] = u'旅行社'
    TR_TV_df[u'年月'] = month
    TR_TV_df[u'渠道'] = 'TV'
    # print(TR_TV_df.isnull().sum())
    print(TR_TV_df.shape)
    # print(TR_TV_df.head())
    # 导入 旅行社_INT表
    TR_INT_df = pd.read_excel(u'./原始表/旅行社_INT_202104.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    TR_INT_df = TR_INT_df.iloc[0:-1]
    TR_INT_df = TR_INT_df.fillna(method='ffill')
    TR_INT_df[u'公司'] = u'旅行社'
    TR_INT_df[u'年月'] = month
    TR_INT_df[u'渠道'] = '新媒体'
    # print(TR_INT_df.isnull().sum())
    print(TR_INT_df.shape)
    # print(TR_INT_df.head())
    # 导入 旅行社_CTL表
    TR_CTL_df = pd.read_excel(u'./原始表/旅行社_CTL_202104.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    TR_CTL_df = TR_CTL_df.iloc[0:-1]
    TR_CTL_df = TR_CTL_df.fillna(method='ffill')
    TR_CTL_df[u'公司'] = u'旅行社'
    TR_CTL_df[u'年月'] = month
    TR_CTL_df[u'渠道'] = 'CTL'
    # print(TR_CTL_df.isnull().sum())
    print(TR_CTL_df.shape)
    # print(TR_CTL_df.head())
    # 导入 贸易公司_全部表
    MAOYI_df = pd.read_excel(u'./原始表/贸易公司_ALL_202104.xls',sheet_name='sheet1',header=15,usecols=[4,5,6,7,8,9,12,13,20,21,22,23,24,25,26,27,29,31,33,34,36,37,39,40,42,43,47,48,49,50,52,53,55,56])
    MAOYI_df = MAOYI_df.iloc[0:-1]
    MAOYI_df= MAOYI_df.fillna(method='ffill')
    MAOYI_df[u'公司'] = u'全球购-东方购物贸易'
    MAOYI_df[u'年月'] = month
    MAOYI_df[u'渠道'] = '新媒体'
    # print(MAOYI_df.isnull().sum())
    print(MAOYI_df.shape)
    # print(MAOYI_df.head())
    # 合并所有表格
    ALL_merge_df = pd.concat([TV_df,INT_df,CTL_df,OT_df,TR_TV_df,TR_INT_df,TR_CTL_df,MAOYI_df])
    # print(ALL_merge_df.isnull().sum())
    print(ALL_merge_df.shape)
    # print(ALL_merge_df.head())
    # 处理 商品区分
    # ALL_merge_df['MD号码'] = ALL_merge_df['MD号码'].astype(np.object)
    # for k in ALL_merge_df['MD号码']:
    #     if k.startswith('I'):
    #         ALL_merge_df['商品区分'] = 'IC商品'
    #     else:
    #         ALL_merge_df['商品区分'] = 'TV商品'
    # print(ALL_merge_df.isnull().sum())
    # print(ALL_merge_df.shape)
    # print(ALL_merge_df.head())
    # 导出为表格
    ALL_merge_df.to_excel(u'./ALL_merge_table.xlsx', sheet_name='table', index=False, encoding='utf-8')
    print(u'所有 表格合并、处理完成！!')


if __name__ == '__main__':

    month = '202104'
   # merge_INT_tables()
    table_process(month)
