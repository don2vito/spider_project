import pandas as pd
import json

# 假设你的JSON数据存储在文件中，文件名为 "20250101-0123视频号明细数据.json"
file_path = "20250101-0123视频号明细数据.json"

# 读取JSON文件
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# 提取所需的字段
details = data["details"]
columns = ["商品标题", "成交订单数", "成交金额"]
extracted_data = [[item[3], item[13], item[14]] for item in details]

# 创建DataFrame
df = pd.DataFrame(extracted_data, columns=columns)

# 保存为Excel文件
output_file = "extracted_data.xlsx"
df.to_excel(output_file, index=False, encoding="utf-8")

print(f"数据已成功保存到 {output_file}")