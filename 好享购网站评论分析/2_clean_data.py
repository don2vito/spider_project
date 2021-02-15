import numpy as np
import pandas as pd
import os
import jieba
import warnings
import time

def merge_comments_lists():
    file_names = os.listdir('./data_list/comments_data')
    frames = []
    for file_name in file_names:
        df = pd.read_csv(os.path.join('./data_list/comments_data', file_name), sep=',', encoding='utf-8', engine='python')
        # print(df.head())
        frames.append(df)
    # print(frames)
    result = pd.concat(frames, join_axes=[df.columns])
    # print(result.head())
    output_path = os.path.join('./data_list', '2_1_hao24_comments_list.csv')
    result.to_csv(output_path, index=False, encoding='utf-8', sep=',', header=True,columns=['commContent', 'commGrade', 'commScore','commTime','custNm','shopNm','item_code'])
    print('共生成数据{}行，{}列'.format(result.shape[0], result.shape[1]))
    print('《评论表》 合并成功！！')

def join_comments_lists():
    result = pd.read_csv(os.path.join('./data_list', '2_1_hao24_comments_list.csv'), sep=',', encoding='utf-8',engine='python')
    result['item_code'] = pd.to_numeric(result['item_code'], errors='coerce')
    items_list_df = pd.read_csv('./data_list/1_3_item_list.csv', sep=',', encoding='utf-8', engine='python')
    items_list_df['item_code'] = pd.to_numeric(items_list_df['item_code'], errors='coerce')
    # print(items_list_df.head())
    df_result = pd.merge(result, items_list_df, how='left', left_on='item_code', right_on='item_code')
    catelog_list_df = pd.read_excel(os.path.join('./data_list', '1_2_catelog_list_after_add.xlsx'), sheet_name='catelog_list',encoding='utf-8', header=0)
    df_merge = pd.merge(df_result, catelog_list_df, how='left', left_on='cat_code', right_on='third_level_id')
    df_merge.to_csv('./data_list/2_2_hao24_comments_list_joined.csv', index=False, encoding='utf-8', sep=',', header=True,columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price','commContent', 'commGrade', 'commScore','commTime','custNm','shopNm'])
    print('共生成数据{}行，{}列'.format(df_merge.shape[0], df_merge.shape[1]))
    print('《评论表》 关联成功！！')

def duplicate_comments_lists():
    df_merge = pd.read_csv('./data_list/2_2_hao24_comments_list_joined.csv', sep=',', encoding='utf-8', engine='python')
    df_duplicate = df_merge.drop_duplicates()
    df_duplicate = df_duplicate[df_duplicate['commContent'] != '评价方未及时作出评价，系统默认好评']
    df_duplicate.to_csv('./data_list/2_3_hao24_comments_list_duplicated.csv', index=False, encoding='utf-8', sep=',',header=True, columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price','commContent', 'commGrade', 'commScore','commTime','custNm','shopNm'])
    print('共生成数据{}行，{}列'.format(df_duplicate.shape[0], df_duplicate.shape[1]))
    print('《评论表》 去重及剔除脏数据成功！！')

def machine_cut_words():
    data_comments = pd.read_csv('./data_list/2_3_hao24_comments_list_duplicated.csv', sep=',', header=0, encoding='utf-8',engine='python')
    # data_test = data.iloc[:101,:]
    # print(f'数据框的列名是： {data_comments.columns.values.tolist()}\n')
    # print(data_comments.head())
    data_comments['item_code'] = data_comments['item_code'].astype(str)
    data_duplicate_words = pd.DataFrame(data_comments)
    data_duplicate_words['seg_comment'] = data_duplicate_words['commContent'].apply(cut_words)
    # print(df.head())
    data_duplicate_words.to_csv('./data_list/2_4_hao24_comments_list_cutwords.csv', encoding='utf-8', index=False,sep=',',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price','commContent', 'commGrade', 'commScore','commTime','custNm','shopNm', 'seg_comment'])
    print('共生成数据{}行，{}列'.format(data_duplicate_words.shape[0], data_duplicate_words.shape[1]))
    print('《评论表》 语料机械压缩成功！！')

def cut_words(x):
    text = jieba.lcut(x)
    text_duplicated = []
    text_join = []
    for i in text:
        if not i in text_duplicated:
            text_duplicated.append(i)
            text_join = "".join(text_duplicated)
            text_join = text_join.replace('.','')
            text_join = text_join.replace('\n', '')
    # print(text_join)
    return text_join

def clean_comments_lists():
    data_duplicate_words = pd.read_csv('./data_list/2_4_hao24_comments_list_cutwords.csv', sep=',', encoding='utf-8',engine='python')
    bool_index = ((data_duplicate_words['seg_comment'].str.len() >= 14) & (data_duplicate_words['seg_comment'] != '"续购，速达。'))
    data_cleaned = data_duplicate_words[bool_index]
    # data_cleaned['item_code'] = data_cleaned['item_code'].apply(lambda x: str(x).split('.')[0])
    data_cleaned['year'] = data_cleaned['commTime'].apply(lambda x: str(x).split('-')[0])
    data_cleaned['month'] = data_cleaned['commTime'].apply(lambda x: str(x).split('-')[1])
    data_cleaned['day'] = data_cleaned['commTime'].apply(lambda x: str(x).split('-')[-1])
    data_cleaned['year_month'] = data_cleaned['commTime'].apply(lambda x: str(x)[:-3])
    data_cleaned['comm_len'] = data_cleaned['seg_comment'].apply(lambda x: len(str(x)))
    data_cleaned= data_cleaned.fillna(method='ffill')
    data_cleaned['year'] = data_cleaned['year'].astype(str)
    data_cleaned['month'] = data_cleaned['month'].astype(str)
    data_cleaned['day'] = data_cleaned['day'].astype(str)
    data_cleaned['item_code'] = data_cleaned['item_code'].astype(str)
    data_cleaned.to_csv('./data_list/2_5_hao24_comments_list_cleaned.csv', encoding='utf-8', index=False, sep=',',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])
    print('共生成数据{}行，{}列'.format(data_cleaned.shape[0], data_cleaned.shape[1]))
    print('《评论表》 清洗完成！！')

def describe_comments_lists():
    cleaned_df = pd.read_csv('./data_list/2_5_hao24_comments_list_cleaned.csv', sep=',', encoding='utf-8',engine='python')
    cleaned_df['year'] = cleaned_df['year'].astype(str)
    cleaned_df['month'] = cleaned_df['month'].astype(str)
    cleaned_df['day'] = cleaned_df['day'].astype(str)
    cleaned_df['item_code'] = cleaned_df['item_code'].astype(str)
    print('查看缺失值：\n{}'.format(cleaned_df.isnull().sum()))
    print('查看年月分布：\n{}'.format(pd.pivot_table(cleaned_df,index=['year','month'],values=['seg_comment'],aggfunc=[len])))
    print('查看一级类目分布：\n{}'.format(pd.pivot_table(cleaned_df, index=['one_level'], values=['seg_comment'], aggfunc=[len])))
    print('查看评论分类分布：\n{}'.format(pd.pivot_table(cleaned_df, index=['commScore'], values=['seg_comment'], aggfunc=[len])))
    print('数据描述性分布如下：\n{}'.format(cleaned_df.describe()))
    print('数据基本信息如下：')
    print(cleaned_df.info())

if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('precision', 3)

    warnings.filterwarnings('ignore')

    time_begin = time.time()
    '''
    # 步骤一：合并所有小分类的评论表（2_1_hao24_comments_list.csv）
    merge_comments_lists()

    # 步骤二：评论表关联（2_2_hao24_comments_list_joined.csv）
    join_comments_lists()
    
    # 步骤三：评论表去重及剔除脏数据（2_3_hao24_comments_list_duplicated.csv）
    duplicate_comments_lists()
    
    # 步骤四：语料机械压缩（2_4_hao24_comments_list_cutwords.csv）
    machine_cut_words()
    
    # 步骤五：评论表清洗（2_5_hao24_comments_list_cleaned.csv）
    clean_comments_lists()
    '''
    # 步骤六：评论表的描述性统计
    describe_comments_lists()

    time_end = time.time()
    print('运行耗时 {:.2f}秒'.format(time_end - time_begin))