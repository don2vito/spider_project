import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
import time
from snownlp import SnowNLP
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import uniform
import requests
import json
import hashlib
import random
import string
from urllib.parse import quote
import sys
import urllib.request
import urllib.parse
import base64

def model_classification():
    df = pd.read_csv('./data_list/3_4_hao24_comments_list_xunfeiapi.csv', sep=',', header=0, engine='python', encoding='utf-8')

    df.to_csv('./data_list/3_2_hao24_comments_list_classificated.csv', sep=',', header=True, index=False, encoding='utf-8',
              columns=['cat_code', 'one_level', 'second_level', 'third_level', 'item_code', 'item_name', 'price',
                       'seg_comment', 'comm_len', 'sentiment_score', 'commGrade', 'commScore', 'commTime', 'custNm',
                       'shopNm', 'year', 'month', 'day', 'year_month'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('《评论表》 无监督机器学习分类完成！！')

def model_compare():
    df = pd.read_csv('./data_list/3_5_hao24_comments_list_classificated.csv', sep=',', header=0, engine='python', encoding='utf-8')



def snownlp_sentiment():
    # 导入数据
    df = pd.read_csv('./data_list/2_5_hao24_comments_list_cleaned.csv', sep=',', header=0, engine='python', encoding='utf-8')
    # print('导入数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    # print('数据源导入成功！！')

    # 提取数据
    text = [i for i in df['seg_comment']]

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
    df['snownlp_sentiment_score'] = newsenti

    # 导出数据
    df.to_csv('./data_list/3_1_hao24_comments_list_snownlp.csv', sep=',', header=True, index=False, encoding='utf-8',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','snownlp_sentiment_score','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('《评论表》 snownlp情感打分完成！！')

def baidunlp_sentiment():
    API_Key = '9QmecQmsb1BKZ0LIP14wz8k9'
    Secret_Key = 'azIGamsyFB4vHeND6VunEM6emm2FGDYl'
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(API_Key,Secret_Key)
    res1 = requests.post(host)
    json_data1 = json.loads(res1.text)
    token = json_data1['access_token']
    # print(token)
    # token = '25.7167bbdd425b159b1d0f8fa22955ebb9.315360000.1881750640.282335-17060024'

    df = pd.read_csv('./data_list/3_1_hao24_comments_list_snownlp.csv', sep=',', header=0, engine='python',encoding='utf-8')
    url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token={}'.format(token)
    data = [i for i in df['seg_comment']]
    newsenti = []
    try:
        for i in range(len(df)):
            content = str(df['seg_comment'][i]).encode(encoding = 'utf-8').decode(encoding = 'utf-8')
            # print(content)
            content_json = {'text':content}
            content = json.dumps(content_json)
            # print(content)
            res2 = requests.post(url,data=content,headers={'Content-Type':'application/json; charset=UTF-8'},verify=False)
            json_data2 = json.loads(res2.text)
            # print(json_data2)
            sentiment = json_data2['items'][0]['positive_prob']
            print(i, ' | ', json.loads(content)['text'],' | ',sentiment)
            newsenti.append(sentiment)
            time.sleep(0.7)
    except KeyError:
        pass
    except requests.exceptions.SSLError:
        pass
    df['baiduapi_sentiment_score'] = newsenti

    df.to_csv('./data_list/3_2_hao24_comments_list_baiduapi.csv', sep=',', header=True, index=False, encoding='utf-8',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','snownlp_sentiment_score','baiduapi_sentiment_score','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('《评论表》 baidu api情感打分完成！！')
    print(df.baiduapi_sentiment_score.isnull().sum())

def curlmd5(src):
    m = hashlib.md5(src.encode('UTF-8'))
    # 将得到的MD5值所有字符转换成大写
    return m.hexdigest().upper()

def get_params(plus_item):
    global params
    #请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效）  
    t = time.time()
    time_stamp=str(int(t))
    # 请求随机字符串，用于保证签名不可预测  
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key  
    app_id='2120940787'
    app_key='sCwfrAJgTs0nQUcu'
    params = {'app_id':app_id,
              'text':plus_item,
              'time_stamp':time_stamp,
              'nonce_str':nonce_str,
             }
    sign_before = ''
    #要对key排序再拼接
    for key in sorted(params):
        # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8。quote默认大写。
        sign_before += '{}={}&'.format(key,quote(params[key], safe=''))
    # 将应用密钥以app_key为键名，拼接到字符串sign_before末尾
    sign_before += 'app_key={}'.format(app_key)
    # 对字符串sign_before进行MD5运算，得到接口请求签名  
    sign = curlmd5(sign_before)
    params['sign'] = sign
    time.sleep(1.3)
    return params

def get_sentiments(comments):
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textpolar"
    comments = comments.encode('utf-8')
    payload = get_params(comments)
    r = requests.post(url, data=payload)
    return r.json()['data']['confd']

def tencentnlp_sentiment():
    df = pd.read_csv('./data_list/3_2_hao24_comments_list_baiduapi.csv', sep=',', header=0, engine='python',encoding='utf-8')
    # print(df.columns)
    data = [i for i in df['seg_comment']]
    newsenti = []
    try:
        for i in range(len(df)):
            content = str(df['seg_comment'][i]).encode(encoding='utf-8').decode(encoding='utf-8')
            # print(content)
            sentiment = get_sentiments(content)
            print(i, ' | ', content,' | ',sentiment)
            newsenti.append(sentiment)
            # time.sleep(0.2)
    except KeyError:
        pass
    except requests.exceptions.SSLError:
        pass
    df['tencentapi_sentiment_score'] = newsenti

    df.to_csv('./data_list/3_3_hao24_comments_list_tencentapi.csv', sep=',', header=True, index=False, encoding='utf-8',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','snownlp_sentiment_score','baiduapi_sentiment_score','tencentapi_sentiment_score','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('《评论表》 tencent api情感打分完成！！')
    print(df.tencentapi_sentiment_score.isnull().sum())


def xunfeinlp_sentiment():
    # 接口地址
    url = "http://ltpapi.xfyun.cn/v1/sa"
    # 开放平台应用ID
    x_appid = "5d5d578b"
    # 开放平台应用接口秘钥
    api_key = "bd16b3301c1215d5f1ff78d7fecb58f9"
    # 语言文本
    df = pd.read_csv('./data_list/3_3_hao24_comments_list_tencentapi.csv', sep=',', header=0, engine='python',encoding='utf-8')
    # print(df.columns)
    data = [i for i in df['seg_comment']]
    positive_prob = []
    neutral_prob = []
    negative_prob = []
    try:
        for i in range(len(df)):
        # for i in range(4108,4113):
            if str(df['seg_comment'][i]) == 'comifengnewsclientgold:/call?type=list':  # 这是一行定制代码！！！
                TEXT = '此条作废'
            else:
                TEXT = str(df['seg_comment'][i])

            body = urllib.parse.urlencode({'text': TEXT}).encode('utf-8')
            param = {"type": "dependent"}
            x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
            x_time = str(int(time.time()))
            x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
            x_header = {'X-Appid': x_appid,
                        'X-CurTime': x_time,
                        'X-Param': x_param,
                        'X-CheckSum': x_checksum}
            req = urllib.request.Request(url, body, x_header)
            result = urllib.request.urlopen(req)
            result = result.read().decode('utf-8')
            json_data1 = json.loads(result)
            # print(json_data1)
            sentiment1 = json_data1['data']['sa']
            # print(sentiment1[0])
            sentiment2 = sentiment1[0]['positive_prob']
            sentiment3 = sentiment1[0]['neutral_prob']
            sentiment4 = sentiment1[0]['negative_prob']
            # print(sentiment2)
            print(i, ' | ', TEXT, ' | ', sentiment2, ' | ', sentiment3, ' | ', sentiment4)
            positive_prob.append(sentiment2)
            neutral_prob.append(sentiment3)
            negative_prob.append(sentiment4)
            # time.sleep(0.3)
    except KeyError:
        pass
    except ValueError:
        pass
    except requests.exceptions.SSLError:
        pass
    df['xunfeiapi_positive_prob_sentiment_score'] = positive_prob
    df['xunfeiapi_neutral_prob_sentiment_score'] = neutral_prob
    df['xunfeiapi_negative_prob_sentiment_score'] = negative_prob
    # print(json.loads(result)['data']['sa']['positive_prob'])
    # print(result.decode('utf-8').json()['data']['sa']['positive_prob'])

    df.to_csv('./data_list/3_4_hao24_comments_list_xunfeiapi.csv', sep=',', header=True, index=False, encoding='utf-8',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','snownlp_sentiment_score','baiduapi_sentiment_score','tencentapi_sentiment_score','xunfeiapi_positive_prob_sentiment_score','xunfeiapi_neutral_prob_sentiment_score','xunfeiapi_negative_prob_sentiment_score','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('《评论表》 xunfei api情感打分完成！！')
    print(df.xunfeiapi_positive_prob_sentiment_score.isnull().sum())


if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    pd.set_option('precision', 3)

    plt.rc('font', family='SimHei')
    plt.rcParams['axes.unicode_minus'] = False

    warnings.filterwarnings('ignore')

    time_begin = time.time()
    # content = get_sentiments('我好开心啊')
    # print(content)
    # 步骤一：snownlp情感打分
    # snownlp_sentiment()

    # 步骤二：百度API、腾讯API、讯飞API情感打分
    # baidunlp_sentiment()
    # tencentnlp_sentiment()
    xunfeinlp_sentiment()
    '''
    # 步骤三：使用无监督机器学习方法对评论进行分类
    model_classification()
    
    # 步骤四：模型比较
    model_compare()
    '''
    time_end = time.time()
    print('运行耗时 {:.2f}秒'.format(time_end - time_begin))