import requests
from bs4 import BeautifulSoup
import pandas as pd

# 基础URL模板
base_url = "https://www.onezh.com/zhanhui/{}_0_0_0_20250101/20251231/"

# 初始化一个空列表，用于存储所有展会信息
exhibitions = []

# 添加请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# 循环爬取35个网页
for page in range(1, 36):  # 从第1页到第35页
    url = base_url.format(str(page))
    print(f"正在请求页面：{url}")  # 打印当前请求的URL
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding  # 确保编码正确

    if response.status_code == 200:
    # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有展会信息的容器
        exhibition_items = soup.find_all('div', class_='row')
        
        # 提取展会信息
        for item in exhibition_items:
            # 提取展会名称
            exhibition_name = item.find('a').get('title') if item.find('a') else "未找到展会名称"
            
            # 提取展会时间和展馆信息
            details = item.find_all('em', class_='cgree1')
            if len(details) >= 2:
                # 第一个 <em> 包含展会时间
                exhibition_time = details[1].text.split("展馆：")[0].strip("展会时间：")
                # 第二个 <em> 包含展馆信息
                exhibition_venue = details[1].text.split("展馆：")[1].strip()
            else:
                exhibition_time = "未找到展会时间"
                exhibition_venue = "未找到展馆信息"
                
            # 将提取的信息存储到列表中
            exhibitions.append({
                "展会名称": exhibition_name,
                "展会时间": exhibition_time,
                "展馆": exhibition_venue
            })
            
            # 打印提取的信息
            print(f"展会名称：{exhibition_name}")
            print(f"展会时间：{exhibition_time}")
            print(f"展馆：{exhibition_venue}")
            print("-" * 50)
    else:
        print(f"请求失败，状态码：{response.status_code}")

# 将列表转换为DataFrame
df = pd.DataFrame(exhibitions)

# 保存到excel文件
df.to_excel("2025年全国展会信息.xlsx", index=False, encoding="utf-8-sig")

# 打印DataFrame
print(df)