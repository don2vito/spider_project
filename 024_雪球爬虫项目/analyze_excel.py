import pandas as pd
import os

# 文件路径
file_path = r'd:/project/雪球爬虫项目/1. 图片链接拆分多行.xlsx'

# 读取Excel文件
print(f"正在读取Excel文件: {file_path}")
df = pd.read_excel(file_path)

# 打印文件基本信息
print(f"\n文件基本信息:")
print(f"总行数: {len(df)}")
print(f"总列数: {len(df.columns)}")

# 打印所有列名
print(f"\n所有列名:")
for i, col in enumerate(df.columns, 1):
    print(f"{i}. '{col}'")

# 检查是否存在'总的序号'和'图片链接'列
print(f"\n列存在性检查:")
if '总的序号' in df.columns:
    print("✓ '总的序号' 列存在")
else:
    print("✗ '总的序号' 列不存在")
    print("请检查是否有类似的列名，如'序号'等")

if '图片链接' in df.columns:
    print("✓ '图片链接' 列存在")
else:
    print("✗ '图片链接' 列不存在")
    print("请检查是否有类似的列名")

# 打印前几行数据样本
print(f"\n前5行数据样本:")
print(df.head())

# 检查数据类型和缺失值
print(f"\n数据类型和缺失值统计:")
print(df.info())

# 统计缺失值
print(f"\n各列缺失值统计:")
print(df.isnull().sum())

# 如果列存在，打印一些示例数据
if '总的序号' in df.columns:
    print(f"\n'总的序号'列数据类型: {df['总的序号'].dtype}")
    print(f"'总的序号'列取值范围: {df['总的序号'].min()} - {df['总的序号'].max()}")
    
if '图片链接' in df.columns:
    print(f"\n'图片链接'列数据类型: {df['图片链接'].dtype}")
    # 打印非空的图片链接示例
    non_empty_links = df['图片链接'].dropna()
    if len(non_empty_links) > 0:
        print(f"非空图片链接数量: {len(non_empty_links)}")
        print("前3个图片链接示例:")
        for i, link in enumerate(non_empty_links.head(3), 1):
            print(f"{i}. {link}")

print("\nExcel文件分析完成！")