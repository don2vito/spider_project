import pandas as pd
import json
import os


datas = []

def get_cates_url(datas):
    df = dict()
    result = pd.DataFrame()
    
    for b_data in datas['data']:
        b_name = b_data['name']
        b_id = b_data['id']
        df['大分类'], df['大分类编号'] =  b_name,b_id
        for m_data in b_data['children']:
            m_name = m_data['name']
            m_id = m_data['id']
            df['中分类'], df['中分类编号'] =  m_name,m_id
            for s_data in m_data['children']:
                s_name = s_data['name']
                s_id = s_data['id']
                s_url = 'http://www.ocj.com.cn/itemSearch.html?categoryId=' + str(s_data['id'])
                df['小分类'], df['小分类编号'], df['小分类链接']=  s_name,s_id,s_url
                print('{} 已爬取……'.format(s_name))
                
                table = pd.DataFrame.from_dict(df,orient='index').T
                result = pd.concat([result, table])
    return result

if __name__ == '__main__':
    # 步骤一：爬取分类表
    with open('./0. category_json.json','r',encoding='utf-8') as file:
        datas = json.load(file)
    df_result = get_cates_url(datas)
    output_path = './data_list'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    df_result.to_excel(os.path.join(output_path, 'catelog_list.xlsx'),sheet_name='catelog_list',index=False,columns=['大分类','大分类编号','中分类','中分类编号','小分类','小分类编号','小分类链接'],encoding='utf-8')
    print(df_result.head())
    print('《分类表》爬取完成！！\n')
    
    #  //*[@id="J_app"]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div/span[1]