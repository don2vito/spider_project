import pandas as pd

# 读取新生成的Excel文件
output_file = r'd:/project/雪球爬虫项目/1. 图片链接拆分多行.xlsx'
print(f"正在验证文件: {output_file}")

try:
    # 读取Excel文件
    df = pd.read_excel(output_file)
    print(f"成功读取验证文件，共有 {len(df)} 行数据")
    print(f"数据列: {df.columns.tolist()}")
    
    # 检查是否包含图片序号列
    if '图片序号' not in df.columns:
        print("❌ 验证失败: 未找到'图片序号'列")
    else:
        print("✅ 验证通过: 成功包含'图片序号'列")
    
    # 验证数据完整性
    print("\n验证数据完整性:")
    required_columns = ['序号', '标题', '主链接', '图片链接', '图片序号']
    for col in required_columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            print(f"⚠️  警告: 列 '{col}' 包含 {missing_count} 个空值")
        else:
            print(f"✅ 列 '{col}' 没有空值")
    
    # 验证图片序号递增性
    print("\n验证图片序号递增性:")
    error_count = 0
    for serial in df['序号'].unique():
        # 获取当前序号的所有行
        serial_df = df[df['序号'] == serial].copy()
        # 按图片序号排序
        serial_df_sorted = serial_df.sort_values('图片序号')
        # 检查是否从1开始递增
        expected_sequence = list(range(1, len(serial_df) + 1))
        actual_sequence = serial_df_sorted['图片序号'].tolist()
        
        if expected_sequence != actual_sequence:
            print(f"❌ 序号 {serial} 的图片序号不连续: {actual_sequence}")
            error_count += 1
    
    if error_count == 0:
        print("✅ 所有序号的图片序号都正确递增")
    else:
        print(f"❌ 发现 {error_count} 个序号的图片序号序列有误")
    
    # 显示一些随机行来检查数据对应关系
    print("\n随机抽取几行数据检查对应关系:")
    sample_rows = df.sample(min(5, len(df)))
    for _, row in sample_rows.iterrows():
        print(f"序号: {row['序号']}, 图片序号: {row['图片序号']}, 标题前20字符: {str(row['标题'])[:20]}...")
    
    # 统计每个序号对应的图片数量分布
    print("\n各序号对应的图片数量分布:")
    image_counts = df.groupby('序号').size().value_counts().sort_index()
    for count, freq in image_counts.items():
        print(f"有 {freq} 个序号包含 {count} 张图片")
    
    print("\n🎉 文件验证完成！")
    
except Exception as e:
    print(f"验证过程中出错: {e}")
    import traceback
    traceback.print_exc()