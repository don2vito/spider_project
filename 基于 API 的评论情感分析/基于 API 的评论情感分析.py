from snownlp import SnowNLP
import requests
import json
import hashlib
import random
import string
import sys
import urllib.request
import urllib.parse
import base64
from urllib.parse import quote

# 利用 snownlp 库进行情感打分
def snownlp_sentiment():
    # 导入数据
    df = pd.read_csv('./data_list/2_5_hao24_comments_list_cleaned.csv', sep=',', header=0, engine='python', encoding='utf-8')

    # 提取数据
    text = [i for i in df['seg_comment']]

    # 遍历每条评论进行情感预测打分
    newsenti = []
    for i in range(len(df)):
        s = SnowNLP(df['seg_comment'][i])
        newsenti.append(s.sentiments)
    df['snownlp_sentiment_score'] = newsenti
    
     # 导出数据
    df.to_csv('./data_list/3_1_hao24_comments_list_snownlp.csv', sep=',', header=True, index=False, encoding='utf-8',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','snownlp_sentiment_score','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('《评论表》 snownlp 情感打分完成！！')

# 使用百度 API 进行情感打分
def baidunlp_sentiment():
    API_Key = '你申请的API_KEY'
    Secret_Key = '你申请的Secret_Key'
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(API_Key,Secret_Key)
    res1 = requests.post(host)
    json_data1 = json.loads(res1.text)
    token = json_data1['access_token']

    df = pd.read_csv('./data_list/3_1_hao24_comments_list_snownlp.csv', sep=',', header=0, engine='python',encoding='utf-8')
    url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token={}'.format(token)
    data = [i for i in df['seg_comment']]
    newsenti = []
    try:
        for i in range(len(df)):
            content = str(df['seg_comment'][i]).encode(encoding = 'utf-8').decode(encoding = 'utf-8')
            content_json = {'text':content}
            content = json.dumps(content_json)
            res2 = requests.post(url,data=content,headers={'Content-Type':'application/json; charset=UTF-8'},verify=False)
            json_data2 = json.loads(res2.text)
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
    print('《评论表》 baidu api 情感打分完成！！')

# 使用腾讯 API 进行情感打分
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
    app_id='你申请的app_id'
    app_key='你申请的app_key'
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
    data = [i for i in df['seg_comment']]
    newsenti = []
    try:
        for i in range(len(df)):
            content = str(df['seg_comment'][i]).encode(encoding='utf-8').decode(encoding='utf-8')
            sentiment = get_sentiments(content)
            newsenti.append(sentiment)
            # time.sleep(0.2)
    except KeyError:
        pass
    except requests.exceptions.SSLError:
        pass
    df['tencentapi_sentiment_score'] = newsenti

    df.to_csv('./data_list/3_3_hao24_comments_list_tencentapi.csv', sep=',', header=True, index=False, encoding='utf-8',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','snownlp_sentiment_score','baiduapi_sentiment_score','tencentapi_sentiment_score','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))
    print('《评论表》 tencent api 情感打分完成！！')
    print(df.tencentapi_sentiment_score.isnull().sum())

# 使用讯飞 API 进行情感打分
def xunfeinlp_sentiment():    # 接口地址    
    url = "http://ltpapi.xfyun.cn/v1/sa"    # 开放平台应用ID    
    x_appid = "你申请的appid"    # 开放平台应用接口秘钥    
    api_key = "你申请的api_key"    # 语言文本    
    df = pd.read_csv('./data_list/3_3_hao24_comments_list_tencentapi.csv', sep=',', header=0, engine='python',encoding='utf-8')    
    # print(df.columns)    
    data = [i for i in df['seg_comment']]    
    positive_prob = []    
    neutral_prob = []    
    negative_prob = []    
    try:        
        for i in range(len(df)):            
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
           sentiment1 = json_data1['data']['sa']            
           sentiment2 = sentiment1[0]['positive_prob']            
           sentiment3 = sentiment1[0]['neutral_prob']            
           sentiment4 = sentiment1[0]['negative_prob']            
           print(i, ' | ', TEXT, ' | ', sentiment2, ' | ', sentiment3, ' | ', sentiment4)            
           positive_prob.append(sentiment2)            
           neutral_prob.append(sentiment3)            
           negative_prob.append(sentiment4)    
    except KeyError:        
        pass    
    except ValueError:        
        pass    
    except requests.exceptions.SSLError:        
        pass    
    df['xunfeiapi_positive_prob_sentiment_score'] = positive_prob    
    df['xunfeiapi_neutral_prob_sentiment_score'] = neutral_prob    
    df['xunfeiapi_negative_prob_sentiment_score'] = negative_prob    
    df.to_csv('./data_list/3_4_hao24_comments_list_xunfeiapi.csv', sep=',', header=True, index=False, encoding='utf-8',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','snownlp_sentiment_score','baiduapi_sentiment_score','tencentapi_sentiment_score','xunfeiapi_positive_prob_sentiment_score','xunfeiapi_neutral_prob_sentiment_score','xunfeiapi_negative_prob_sentiment_score','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])    
    print('导出数据共有{}行，{}列！'.format(df.shape[0], df.shape[1]))   
    print('《评论表》 xunfei api 情感打分完成！！')