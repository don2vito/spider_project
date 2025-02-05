import re
import pandas as pd

# 读取文件内容
with open("快团团数据.txt", "r", encoding="utf-8") as file:
    text = file.read()

# 定义正则表达式
pattern = r'快团团日报：(\d+)\s+东方购物（订阅领🧧）,订购数量：(\d+)单，订购人数：(\d+)个，订购金额：([\d.]+)元，利润：([\d.-]+)元；\s+【东方购物】番茄团,订购数量：(\d+)单，订购人数：(\d+)个，订购金额：([\d.]+)元，利润：([\d.-]+)元。'

# 查找所有匹配
matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)

# 创建DataFrame
columns = [
    "日期", "东方购物订购数量", "东方购物订购人数", "东方购物订购金额", "东方购物利润",
    "番茄团订购数量", "番茄团订购人数", "番茄团订购金额", "番茄团利润"
]
df = pd.DataFrame(matches, columns=columns)

# 输出完整的表格
print(df)

# 保存到Excel文件
df.to_excel("快团团日报数据.xlsx", index=False)
print("数据已保存到快团团日报数据.xlsx")