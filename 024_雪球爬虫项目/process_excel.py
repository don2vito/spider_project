import pandas as pd
import os

# 设置中文字体支持
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

# 读取原始Excel文件
file_path = r'd:/project/雪球爬虫项目/0. 初步整理.xlsx'
print(f"正在读取文件: {file_path}")

try:
    # 读取Excel文件
    df = pd.read_excel(file_path)
    print(f"成功读取文件，共有 {len(df)} 行数据")
    print("数据列名:", df.columns.tolist())
    
    # 显示前几行数据来确认结构
    print("\n前5行数据:")
    print(df.head())
    
    # 检查'图片链接'列是否存在
    if '图片链接' not in df.columns:
        print("错误: 未找到'图片链接'列")
        exit(1)
    
    print("\n开始处理图片链接拆分...")
    
    # 创建新的DataFrame用于存储拆分后的数据
    new_data = []
    
    # 遍历原始数据的每一行
    for _, row in df.iterrows():
        # 获取当前行的基本信息
        serial_number = row['序号']
        title = row['标题']
        main_link = row['主链接']
        image_links = row['图片链接']
        
        # 检查图片链接是否为字符串类型
        if pd.notna(image_links):
            # 将图片链接按逗号拆分
            if isinstance(image_links, str) and ',' in image_links:
                links = [link.strip() for link in image_links.split(',')]
            else:
                # 如果没有逗号或不是字符串，视为单个链接
                links = [str(image_links)] if pd.notna(image_links) else ['']
            
            # 为每个链接创建新行，并添加图片序号
            for img_idx, link in enumerate(links, 1):
                new_data.append({
                    '序号': serial_number,
                    '标题': title,
                    '主链接': main_link,
                    '图片链接': link,
                    '图片序号': img_idx
                })
        else:
            # 处理空图片链接的情况
            new_data.append({
                '序号': serial_number,
                '标题': title,
                '主链接': main_link,
                '图片链接': '',
                '图片序号': 1
            })
    
    # 创建新的DataFrame
    new_df = pd.DataFrame(new_data)
    print(f"图片链接拆分完成，生成了 {len(new_df)} 行数据")
    
    # 显示前几行拆分后的数据
    print("\n拆分后的前10行数据:")
    print(new_df.head(10))
    
    # 检查是否有成功拆分的行（包含多个图片的行）
    multi_image_count = 0
    for serial in df['序号'].unique():
        count = len(new_df[new_df['序号'] == serial])
        if count > 1:
            multi_image_count += 1
            print(f"序号 {serial} 包含 {count} 个图片链接")
    
    print(f"\n共有 {multi_image_count} 行数据包含多个图片链接")
    
    # 保存到新的Excel文件
    output_file = r'd:/project/雪球爬虫项目/1. 图片链接拆分多行.xlsx'
    print(f"\n正在保存结果到: {output_file}")
    
    # 保存DataFrame到Excel文件
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        new_df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    print(f"\n文件保存成功！新文件包含 {len(new_df)} 行数据")
    print(f"文件路径: {output_file}")
    
except Exception as e:
    print(f"处理文件时出错: {e}")
    import traceback
    traceback.print_exc()