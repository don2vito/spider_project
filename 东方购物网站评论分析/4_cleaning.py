import os
import pandas as pd
import jieba

def join_csv():
    file_names = os.listdir('./output')
    frames = []
    for file_name in file_names:
        df = pd.read_csv(os.path.join('./output',file_name),sep=',',encoding='utf-8',engine='python')
        # print(df.head())
        frames.append(df)
    # print(frames)
    result = pd.concat(frames,join_axes=[df.columns])
    result['item_id'] = result['url'].apply(lambda x:str(x).split('?')[0].split('/')[-1])
    # print(result.head())
    output_path = os.path.join('./data_list','OCJ_comments_list.csv')
    result.to_csv(output_path,index=False,encoding='utf-8',sep=',',header=True,columns=['item_id','url','comment'])
    print('共生成数据{}行，{}列'.format(result.shape[0],result.shape[1]))
    print('合并CSV成功！！')

def merge_csv():
    result = pd.read_csv(os.path.join('./data_list','OCJ_comments_list.csv'),sep=',',encoding='utf-8',engine='python')
    result['item_id'] = pd.to_numeric(result['item_id'], errors='coerce')
    items_list_df = pd.read_csv('./data_list/items_list.csv',sep=',',encoding='utf-8',engine='python')
    items_list_df['cates_url'] = items_list_df['cate_url'].apply(lambda x: str(x).split('?')[0])
    items_list_df['item_code'] = pd.to_numeric(items_list_df['item_code'], errors='coerce')
    # print(items_list_df.head())
    df_result = pd.merge(result, items_list_df, how='inner',left_on='item_id',right_on='item_code')
    # df_result.to_csv('./data_list/data_list_after_merge.csv', index=False,encoding='utf-8', sep=',', header=True,columns=['item_id','url','comment','pro_name','pro_price','cates_url'])
    catelog_list_df = pd.read_excel(os.path.join('./data_list','catelog_list.xlsx'),sheet_name='catelog_list',encoding='utf-8',header=0)
    df_merge = pd.merge(df_result,catelog_list_df, how='inner',left_on='cates_url',right_on='cates_url')
    df_merge.to_csv('./data_list/data_list_after_merge.csv', index=False,encoding='utf-8', sep=',', header=True,columns=['item_id','title','cate','pro_name','pro_price','comment'])
    print('共生成数据{}行，{}列'.format(df_merge.shape[0], df_merge.shape[1]))
    print('关联CSV成功！！')

def duplicate_csv():
    df_merge = pd.read_csv('./data_list/data_list_after_merge.csv',sep=',',encoding='utf-8',engine='python')
    df_duplicate = df_merge.drop_duplicates()
    df_duplicate.to_csv('./data_list/data_list_after_duplicated.csv', index=False,encoding='utf-8', sep=',', header=True,columns=['item_id','title','cate','pro_name','pro_price','comment'])
    print('共生成数据{}行，{}列'.format(df_duplicate.shape[0], df_duplicate.shape[1]))
    print('CSV全量去重成功！！')

def cut_words(x):
    text = jieba.lcut(x)
    text_duplicated = []
    text_join = []
    for i in text:
        if not i in text_duplicated:
            text_duplicated.append(i)
            text_join = "".join(text_duplicated)
    # print(text_join)
    return text_join

def data_clean():
    data_duplicate_words = pd.read_csv('./data_list/data_list_after_duplicated_words.csv',sep=',',encoding='utf-8',engine='python')
    bool_index = (data_duplicate_words['seg_comment'].str.len() > 14)
    data_cleaned = data_duplicate_words[bool_index]
    data_cleaned['item_id'] = data_cleaned['item_id'].apply(lambda x: str(x).split('.')[0])
    data_cleaned.to_csv('./data_list/data_list_after_cleaned.csv', encoding='utf-8', index=False, sep=',',columns=['item_id','title','cate','pro_name','pro_price','comment','seg_comment'])
    print('共生成数据{}行，{}列'.format(data_cleaned.shape[0], data_cleaned.shape[1]))
    print('数据清洗完成！！')

if __name__ == '__main__':
    # 步骤一：合并CSV
    join_csv()
    # 步骤二：关联CSV
    merge_csv()
    # 步骤三：数据去重
    duplicate_csv()
    # 步骤四：语料机械压缩
    data_comments = pd.read_csv('./data_list/data_list_after_duplicated.csv', sep=',', header=0, encoding='utf-8', engine='python')
    # data_test = data.iloc[:101,:]
    # print(f'数据框的列名是： {data_comments.columns.values.tolist()}\n')
    # print(data_comments.head())
    data_duplicate_words = pd.DataFrame(data_comments.astype(str))
    data_duplicate_words['seg_comment'] = data_duplicate_words['comment'].apply(cut_words)
    # print(df.head())
    data_duplicate_words.to_csv('./data_list/data_list_after_duplicated_words.csv', encoding='utf-8', index=False, sep=',',columns=['item_id','title','cate','pro_name','pro_price','comment','seg_comment'])
    print('共生成数据{}行，{}列'.format(data_duplicate_words.shape[0], data_duplicate_words.shape[1]))
    print('评论语料机械压缩成功！！')
    # 步骤五：数据清洗
    data_clean()
