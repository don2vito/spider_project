#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：处理有限数量的图片以验证PDF生成功能
"""

import os
from image_processor import ImageProcessor
from pdf_generator import PDFGenerator

def main():
    # 配置参数
    image_folder = r"d:\project\雪球爬虫项目\雪球图书 - 进阶吧 投资者"
    output_pdf = os.path.join(os.getcwd(), "测试_进阶吧 投资者.pdf")
    
    print(f"图片文件夹: {image_folder}")
    print(f"输出PDF文件: {output_pdf}")
    print("-"*80)
    
    # 获取排序后的图片列表
    processor = ImageProcessor(image_folder)
    sorted_images = processor.get_sorted_images()
    
    print(f"找到 {len(sorted_images)} 张图片")
    
    # 只处理前50张图片进行测试
    test_images = sorted_images[:50]
    print(f"测试处理前 {len(test_images)} 张图片")
    
    # 验证图片
    valid_images, invalid_images = processor.validate_images(test_images)
    print(f"有效图片: {len(valid_images)}")
    
    # 生成PDF
    generator = PDFGenerator(output_pdf)
    success = generator.image_to_pdf(valid_images)
    
    if success and os.path.exists(output_pdf):
        file_size = os.path.getsize(output_pdf) / 1024 / 1024  # MB
        print(f"✅ 测试PDF生成成功！")
        print(f"文件大小: {file_size:.2f} MB")
        return True
    else:
        print("❌ 测试PDF生成失败")
        return False

if __name__ == "__main__":
    main()