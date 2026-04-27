#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证PDF文件的页数是否与原始图片数量一致
"""

import os
from PyPDF2 import PdfReader

def verify_pdf_pages(pdf_path, expected_pages):
    """
    验证PDF文件的页数
    
    Args:
        pdf_path: PDF文件路径
        expected_pages: 期望的页数
        
    Returns:
        dict: 包含验证结果的字典
    """
    try:
        print(f"验证PDF文件: {pdf_path}")
        
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "message": f"错误: PDF文件不存在 - {pdf_path}",
                "actual_pages": 0
            }
        
        # 计算文件大小
        file_size = os.path.getsize(pdf_path) / 1024 / 1024  # MB
        print(f"PDF文件大小: {file_size:.2f} MB")
        
        # 读取PDF文件并获取页数
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            actual_pages = len(reader.pages)
        
        print(f"实际页数: {actual_pages}")
        print(f"期望页数: {expected_pages}")
        
        # 验证页数是否一致
        if actual_pages == expected_pages:
            return {
                "success": True,
                "message": f"✅ PDF页数验证通过！实际页数 {actual_pages} 与期望页数 {expected_pages} 一致。",
                "actual_pages": actual_pages,
                "file_size_mb": file_size
            }
        else:
            difference = actual_pages - expected_pages
            direction = "多" if difference > 0 else "少"
            return {
                "success": False,
                "message": f"❌ PDF页数验证失败！实际页数 {actual_pages} 比期望页数 {expected_pages} {direction} {abs(difference)} 页。",
                "actual_pages": actual_pages,
                "file_size_mb": file_size
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ 验证过程中出错: {str(e)}",
            "actual_pages": 0
        }

if __name__ == "__main__":
    # 设置要验证的PDF文件路径
    pdf_path = "进阶吧 投资者（1-6册全）.pdf"
    
    # 设置期望的页数（即原始图片数量）
    expected_pages = 1123
    
    print("="*60)
    print("PDF页数验证工具")
    print("="*60)
    
    # 执行验证
    result = verify_pdf_pages(pdf_path, expected_pages)
    
    print("\n" + result["message"])
    print("="*60)
    
    # 设置退出码
    exit_code = 0 if result["success"] else 1
    exit(exit_code)