import os
import time
import xlwings as xw
import jieba.analyse
import pandas as pd
import stylecloud


t1 = time.time()

output_path = './data_tables'
if not os.path.exists(output_path):
    os.makedirs(output_path)
    
pic_path = './pic_output'
if not os.path.exists(pic_path):
    os.makedirs(pic_path)

# 提取关键词
f = pd.ExcelFile(os.path.join(output_path, '5. splited_data.xlsx'))
for i in f.sheet_names:
    df = pd.read_excel(os.path.join(output_path, '5. splited_data.xlsx'),sheet_name=i)
    df['概述'] = df['概述'].astype(str)
    content = (''.join(i for i in df['概述']))
    # print(f'{i} 的概述文本是：\n{content}')
    jieba.add_word('碳中和')
    jieba.add_word('消费者')
    jieba.del_word('CBNData')
    jieba.del_word('Euromonitor')
    jieba.del_word('CAGR')
    jieba.del_word('SKU')
    jieba.del_word('费者')
    jieba.del_word('QuestMobile')
    jieba.analyse.set_stop_words('./常见中文停用词表.txt')
    kws = jieba.analyse.extract_tags(content,topK=20)
    # print(f'{i} 的概述关键词是：\n{kws}')
    text = ' '.join(kws)
    stylecloud.gen_stylecloud(
                                text=text,
                                palette='tableau.BlueRed_6',
                                icon_name='fas fa-apple-alt',
                                font_path='./田英章楷书3500字.ttf',
                                output_name='./pic_output/' + i + '.png',
                                # custom_stopwords=stopwords
                            )
    print(f'已生成《{i}》词云图！！')

t2 = time.time()

print('运行共耗时 {:.1f}秒'.format(t2 - t1))