import pandas as pd
import snownlp
from snownlp import sentiment
from snownlp import SnowNLP
import jieba
import numpy as np
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
from PIL import Image
from matplotlib import pyplot as plt
import os
import collections
import pyecharts

def snownlp_sentiment():
    # 导入数据
    df = pd.read_csv('./data_list/data_list_after_cleaned.csv',sep=',',header=0,engine='python',encoding='utf-8')
    print('导入数据共有{}行，{}列！'.format(df.shape[0],df.shape[1]))
    print('数据源导入成功！！')

    # 提取数据
    text0 = df['seg_comment']
    text1 = [i for i in text0]

    # 遍历每条评论进行情感预测打分
    newsenti = []
    for i in range(len(df)):
        s = SnowNLP(df['seg_comment'][i])
        # print(df['seg_comment'][i], s.sentiments)
        newsenti.append(s.sentiments)
        # if (i >= 0.6):
        #     newsenti.append(1)
        # else:
        #     newsenti.append(-1)
    df['sentiment_score'] = newsenti

    # 导出数据
    df.to_csv('./data_list/data_list_after_score.csv', sep=',', header=True, index=False,encoding='utf-8',columns=['item_id','title','cate','pro_name','pro_price','seg_comment','sentiment_score'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('评论打分完成！！')

def score_groupby():
    df = pd.read_csv('./data_list/data_list_after_score.csv', sep=',', header=0, engine='python', encoding='utf-8')
    print('导入数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('评分数据导入成功！！')

    group = [0, 0.35, 0.65,1,2]
    df['group'] = pd.cut(df.sentiment_score, group, labels=['差评', '中评', '好评', '好评'],right=False)
    df[df['sentiment_score'] == 1.0]['group'] = '好评'

    df.to_csv('./data_list/data_list_after_groupby.csv', sep=',', header=True, index=False,encoding='utf-8',columns=['item_id','title','cate','pro_name','pro_price','seg_comment','sentiment_score','group'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('评论分类完成！！')

def cut_words_all():
    data = pd.read_csv('./data_list/data_list_after_groupby.csv', sep=',', header=0, encoding='utf-8',engine='python',dtype=str)
    # data = data.iloc[:101, :]
    print('导出数据共有{}行，{}列！'.format(data.shape[0], data.shape[1]))
    print('读取数据源成功！！')
    data_cut_words = pd.DataFrame(data.astype(str))
    # data_cut_words['cut_comment'] = data_duplicate_words['seg_comment'].apply(cut_words)
    # stopwords = load_stopwords()
    stopwords = [line.strip() for line in open('./常见中文停用词表.txt', encoding='gbk').readlines()]
    # 保存全局分词，用于词频统计
    segments = []
    # 普通分词及停用词判断
    for index, row in data_cut_words.iterrows():
        content = row[5]
        # TextRank 关键词抽取，只获取固定词性
        words = jieba.cut(content,cut_all=False)
        splitedStr = ''
        for word in words:
            # 停用词判断，如果当前的关键词不在停用词库中才进行记录
            if word not in stopwords:
                # 记录全局分词
                segments.append({'word': word, 'count': 1})
                splitedStr += word + ' '
    # 将结果数组转为df序列
    dfSg = pd.DataFrame(segments)
    # dfSg.to_csv('./data_list/keywords_count_raw.csv', sep=',', header=True, index=False, encoding='utf-8', columns=['word','count'])
    # 词频统计
    dfWord = pd.pivot_table(dfSg,index=['word'],values=['count'],aggfunc='sum')
    dfWord.reset_index(inplace=True)
    dfWord.sort_values(by='count',ascending=False,inplace=True)
    dfWord = dfWord[dfWord['count'] >= 100]
    # 输出结果
    # print(dfWord.head())
    dfWord.to_csv('./data_list/keywords_count_all.csv', sep=',', header=True, index=False,encoding='utf-8', columns=['word','count'])
    print('导出数据共有{}行，{}列！'.format(dfWord.shape[0], dfWord.shape[1]))
    print('《整体词频统计表》 导出完成！！')

def cut_words_title(title):
    data = pd.read_csv('./data_list/data_list_after_groupby.csv', sep=',', header=0, encoding='utf-8',engine='python',dtype=str)
    data = data[data['title'] == title]
    print('导出数据共有{}行，{}列！'.format(data.shape[0], data.shape[1]))
    print('读取数据源成功！！')
    data_cut_words = pd.DataFrame(data.astype(str))
    # data_cut_words['cut_comment'] = data_duplicate_words['seg_comment'].apply(cut_words)
    # stopwords = load_stopwords()
    stopwords = [line.strip() for line in open('./常见中文停用词表.txt', encoding='gbk').readlines()]
    # 保存全局分词，用于词频统计
    segments = []
    # 普通分词及停用词判断
    for index, row in data_cut_words.iterrows():
        content = row[5]
        # TextRank 关键词抽取，只获取固定词性
        words = jieba.cut(content,cut_all=False)
        splitedStr = ''
        for word in words:
            # 停用词判断，如果当前的关键词不在停用词库中才进行记录
            if word not in stopwords:
                # 记录全局分词
                segments.append({'word': word, 'count': 1})
                splitedStr += word + ' '
    # 将结果数组转为df序列
    dfSg = pd.DataFrame(segments)
    # dfSg.to_csv('./data_list/keywords_count_raw.csv', sep=',', header=True, index=False, encoding='utf-8', columns=['word','count'])
    # 词频统计
    dfWord = pd.pivot_table(dfSg,index=['word'],values=['count'],aggfunc='sum')
    dfWord.reset_index(inplace=True)
    dfWord.sort_values(by='count',ascending=False,inplace=True)
    dfWord = dfWord[dfWord['count'] >= 20]
    # 输出结果
    # print(dfWord.head())
    file_name = title + '_' + 'keywords_count.csv'
    dfWord.to_csv(os.path.join('./data_list',file_name), sep=',', header=True, index=False,encoding='utf-8', columns=['word','count'])
    print('导出数据共有{}行，{}列！'.format(dfWord.shape[0], dfWord.shape[1]))
    print(title + '《词频统计表》 导出完成！！')

def word_cloud_all():
    # 读取文件
    data = pd.read_csv('./data_list/data_list_after_groupby.csv', sep=',', header=0, encoding='utf-8',engine='python',dtype=str)
    # data = data.iloc[:101, :]
    print('导出数据共有{}行，{}列！'.format(data.shape[0], data.shape[1]))
    print('读取数据源成功！！')
    data_cut_words = pd.DataFrame(data.astype(str))
    # data_cut_words['cut_comment'] = data_duplicate_words['seg_comment'].apply(cut_words)
    # stopwords = load_stopwords()
    stopwords = [line.strip() for line in open('./常见中文停用词表.txt', encoding='gbk').readlines()]
    # 保存全局分词，用于词频统计
    segments = []
    # 普通分词及停用词判断
    for index, row in data_cut_words.iterrows():
        content = row[5]
        # TextRank 关键词抽取，只获取固定词性
        words = jieba.cut(content,cut_all=False)
        # splitedStr = ''
        for word in words:
            # 停用词判断，如果当前的关键词不在停用词库中才进行记录
            if word not in stopwords:
                # 记录全局分词
                segments.append(word)
                # splitedStr += word + ' '
    word_counts = collections.Counter(segments) # 对分词做词频统计
    word_counts_top10 = word_counts.most_common(50) # 获取前50最高频的词
    print ('文本词频最高的前50个词是: {}'.format(word_counts_top10)) # 输出检查
    # 设置中文字体
    font_path = os.path.join('C:\Windows\Fonts', '方正中倩简体.ttf')
    # 生成词云
    wc = WordCloud(font_path=font_path, margin=2, scale=2, max_words=200, min_font_size=4,random_state=42, background_color='white', max_font_size=150)
    wc.generate_from_frequencies(word_counts)
    # 获取文本词排序，可调整 stopwords
    # process_word = WordCloud.process_text(wc, text)
    # sort = sorted(process_word.items(), key=lambda e: e[1], reverse=True)
    # 获取文本词频最高的前50个词
    # print('文本词频最高的前50个词是: {}'.format(sort[:50]))
    # 存储并显示图像
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    # 存储图像
    plt.savefig('./data_list/word_cloud_all_output.png', dpi=400)
    plt.show()
    print('整体词云图片 生成完成！！')

def word_cloud_title(title):
    # 读取文件
    data = pd.read_csv('./data_list/data_list_after_groupby.csv', sep=',', header=0, encoding='utf-8',engine='python',dtype=str)
    data = data[data['title'] == title]
    print('导出数据共有{}行，{}列！'.format(data.shape[0], data.shape[1]))
    print('读取数据源成功！！')
    data_cut_words = pd.DataFrame(data.astype(str))
    # data_cut_words['cut_comment'] = data_duplicate_words['seg_comment'].apply(cut_words)
    # stopwords = load_stopwords()
    stopwords = [line.strip() for line in open('./常见中文停用词表.txt', encoding='gbk').readlines()]
    # 保存全局分词，用于词频统计
    segments = []
    # 普通分词及停用词判断
    for index, row in data_cut_words.iterrows():
        content = row[5]
        # TextRank 关键词抽取，只获取固定词性
        words = jieba.cut(content,cut_all=False)
        # splitedStr = ''
        for word in words:
            # 停用词判断，如果当前的关键词不在停用词库中才进行记录
            if word not in stopwords:
                # 记录全局分词
                segments.append(word)
                # splitedStr += word + ' '
    word_counts = collections.Counter(segments) # 对分词做词频统计
    word_counts_top10 = word_counts.most_common(50) # 获取前50最高频的词
    print ('文本词频最高的前50个词是: {}'.format(word_counts_top10)) # 输出检查
    # 设置中文字体
    font_path = os.path.join('C:\Windows\Fonts', '方正中倩简体.ttf')
    # 生成词云
    wc = WordCloud(font_path=font_path, margin=2, scale=2, max_words=200, min_font_size=4,random_state=42, background_color='white', max_font_size=150)
    wc.generate_from_frequencies(word_counts)
    # 获取文本词排序，可调整 stopwords
    # process_word = WordCloud.process_text(wc, text)
    # sort = sorted(process_word.items(), key=lambda e: e[1], reverse=True)
    # 获取文本词频最高的前50个词
    # print('文本词频最高的前50个词是: {}'.format(sort[:50]))
    # 存储并显示图像
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    # 存储图像
    file_name = title + '_' + 'word_cloud_output.png'
    plt.savefig(os.path.join('./data_list',file_name), dpi=400)
    plt.show()
    print(title + '词云图片 生成完成！！')

def describe_data():
    pass

def EDA_all():
    pass

def EDA_title(title):
    pass

if __name__ == '__main__':
    title = str(input('请输入大类名称：'))
    # 步骤一：snownlp对评论进行情感打分
    # snownlp_sentiment()
    # 步骤二：对评论分数进行区间分类（好、中、差评）
    # score_groupby()
    # 步骤三：EDA，生成柱状图或直方图等描述性图（先整体生成一个，再每个大类生成一个图）
    # 对整体进行描述性分析，查看数据的分布情况
    # describe_data()
    # 对整体进行EDA
    # EDA_all()
    # 对大类进行EDA
    # EDA_title(aaa)
    # 步骤四：结巴分词，词频统计，生成词云（先整体生成一个，再每个大类生成一个词云）
    # 对整体词频统计
    # cut_words_all()
    # 分大类词频统计
    # cut_words_title(title)
    # 对整体生成词云
    # word_cloud_all()
    # 分大类生成词云
    # word_cloud_title(title)