import json
import pandas as pd

# 读取JSON文件内容
with open('20250101-0123视频号明细数据.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取字段索引
header = data["header"]
title_idx = header.index("商品标题")
order_idx = header.index("成交订单数")
amount_idx = header.index("成交金额")

# 提取数据
result = []
for detail in data["details"]:
    title = detail[title_idx]
    orders = detail[order_idx] if isinstance(detail[order_idx], (int, float)) else 0
    amount = detail[amount_idx] if isinstance(detail[amount_idx], (int, float)) else 0.0
    result.append({
        "商品标题": title,
        "成交订单数": int(orders),
        "成交金额": float(amount)
    })

# 创建DataFrame并保存为Excel
df = pd.DataFrame(result)
df.to_excel("商品销售数据.xlsx", index=False, engine='openpyxl')

print("Excel文件已生成：商品销售数据.xlsx")