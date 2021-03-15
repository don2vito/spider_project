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

# ���� snownlp �������д��
def snownlp_sentiment():
    # ��������
    df = pd.read_csv('./data_list/2_5_hao24_comments_list_cleaned.csv', sep=',', header=0, engine='python', encoding='utf-8')

    # ��ȡ����
    text = [i for i in df['seg_comment']]

    # ����ÿ�����۽������Ԥ����
    newsenti = []
    for i in range(len(df)):
        s = SnowNLP(df['seg_comment'][i])
        newsenti.append(s.sentiments)
    df['snownlp_sentiment_score'] = newsenti
    
     # ��������
    df.to_csv('./data_list/3_1_hao24_comments_list_snownlp.csv', sep=',', header=True, index=False, encoding='utf-8',columns=['cat_code','one_level','second_level','third_level','item_code','item_name','price', 'seg_comment', 'comm_len','snownlp_sentiment_score','commGrade', 'commScore','commTime','custNm','shopNm','year','month','day','year_month'])
    print('�������ݹ���{}�У�{}�У�'.format(df.shape[0], df.shape[1]))
    print('�����۱� snownlp ��д����ɣ���')

# ʹ�ðٶ� API ������д��
def baidunlp_sentiment():
    API_Key = '�������API_KEY'
    Secret_Key = '�������Secret_Key'
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
    print('�������ݹ���{}�У�{}�У�'.format(df.shape[0], df.shape[1]))
    print('�����۱� baidu api ��д����ɣ���')

# ʹ����Ѷ API ������д��
def curlmd5(src):
    m = hashlib.md5(src.encode('UTF-8'))
    # ���õ���MD5ֵ�����ַ�ת���ɴ�д
    return m.hexdigest().upper()

def get_params(plus_item):
    global params
    #����ʱ������뼶�������ڷ�ֹ�����طţ���֤ǩ��5������Ч��  
    t = time.time()
    time_stamp=str(int(t))
    # ��������ַ��������ڱ�֤ǩ������Ԥ��  
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # Ӧ�ñ�־�������޸ĳ��Լ���id��key  
    app_id='�������app_id'
    app_key='�������app_key'
    params = {'app_id':app_id,
              'text':plus_item,
              'time_stamp':time_stamp,
              'nonce_str':nonce_str,
             }
    sign_before = ''
    #Ҫ��key������ƴ��
    for key in sorted(params):
        # ��ֵƴ�ӹ���value������ҪURL���룬URL�����㷨�ô�д��ĸ������%E8��quoteĬ�ϴ�д��
        sign_before += '{}={}&'.format(key,quote(params[key], safe=''))
    # ��Ӧ����Կ��app_keyΪ������ƴ�ӵ��ַ���sign_beforeĩβ
    sign_before += 'app_key={}'.format(app_key)
    # ���ַ���sign_before����MD5���㣬�õ��ӿ�����ǩ��  
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
    print('�������ݹ���{}�У�{}�У�'.format(df.shape[0], df.shape[1]))
    print('�����۱� tencent api ��д����ɣ���')
    print(df.tencentapi_sentiment_score.isnull().sum())

# ʹ��Ѷ�� API ������д��
def xunfeinlp_sentiment():    # �ӿڵ�ַ    
    url = "http://ltpapi.xfyun.cn/v1/sa"    # ����ƽ̨Ӧ��ID    
    x_appid = "�������appid"    # ����ƽ̨Ӧ�ýӿ���Կ    
    api_key = "�������api_key"    # �����ı�    
    df = pd.read_csv('./data_list/3_3_hao24_comments_list_tencentapi.csv', sep=',', header=0, engine='python',encoding='utf-8')    
    # print(df.columns)    
    data = [i for i in df['seg_comment']]    
    positive_prob = []    
    neutral_prob = []    
    negative_prob = []    
    try:        
        for i in range(len(df)):            
            if str(df['seg_comment'][i]) == 'comifengnewsclientgold:/call?type=list':  # ����һ�ж��ƴ��룡����                
               TEXT = '��������'            
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
    print('�������ݹ���{}�У�{}�У�'.format(df.shape[0], df.shape[1]))   
    print('�����۱� xunfei api ��д����ɣ���')