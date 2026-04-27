#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF验证工具：检查生成的PDF文件是否完整及包含的页面数量
"""

import os
import sys
from PyPDF2 import PdfReader

def verify_pdf(pdf_path):
    """验证PDF文件的完整性和页面数量"""
    print("="*80)
    print(f"开始验证PDF文件: {pdf_path}")
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"❌ 错误: PDF文件不存在 - {pdf_path}")
        return False
    
    # 检查文件大小
    file_size = os.path.getsize(pdf_path)
    print(f"文件大小: {file_size} 字节 ({file_size/1024:.2f} KB)")
    
    # 如果文件太小，可能不完整
    if file_size < 1024:  # 小于1KB
        print("⚠️  警告: PDF文件非常小，可能不完整")
    
    # 尝试打开并读取PDF
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            
            # 获取页面数量
            num_pages = len(reader.pages)
            print(f"PDF页面数量: {num_pages}")
            
            # 获取PDF元信息
            if reader.metadata:
                print("PDF元信息:")
                for key, value in reader.metadata.items():
                    print(f"  {key}: {value}")
            
            # 检查是否有内容
            if num_pages > 0:
                # 检查第一页是否有内容
                first_page = reader.pages[0]
                text_content = first_page.extract_text()
                print(f"\n第一页文本内容长度: {len(text_content)} 字符")
                if len(text_content) > 50:
                    print(f"第一页文本预览: {text_content[:50]}...")
                
                # 检查最后一页
                if num_pages > 1:
                    last_page = reader.pages[-1]
                    last_text = last_page.extract_text()
                    print(f"最后一页文本内容长度: {len(last_text)} 字符")
            
            print("\n✅ PDF文件验证完成")
            return True
            
    except Exception as e:
        print(f"❌ PDF文件验证失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # PDF文件路径
    pdf_path = os.path.join(os.getcwd(), "进阶吧 投资者（1-6册全）.pdf")
    
    # 验证PDF
    success = verify_pdf(pdf_path)
    
    # 分析结果
    if success:
        file_size = os.path.getsize(pdf_path)
        # 根据文件大小提供建议
        if file_size < 1024:
            print("\n📊 分析结论:")
            print("  - PDF文件可能只有基本结构，没有包含完整的图片内容")
            print("  - 建议重新运行主程序或检查图片处理过程")
        elif file_size < 10*1024*1024:  # 小于10MB
            print("\n📊 分析结论:")
            print("  - PDF文件大小适中，但对于1123张图片来说可能不够")
            print("  - 可能部分图片未被正确添加")
        else:
            print("\n📊 分析结论:")
            print("  - PDF文件大小合理，可能包含了大部分图片")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)