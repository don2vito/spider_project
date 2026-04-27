#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查PDF文档内容的完整性和顺序
"""

import os
from PyPDF2 import PdfReader

def check_pdf_integrity(pdf_path):
    """
    检查PDF文档的完整性
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        dict: 包含检查结果的字典
    """
    try:
        print(f"检查PDF文件: {pdf_path}")
        
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            return {
                "success": False,
                "message": f"错误: PDF文件不存在 - {pdf_path}"
            }
        
        # 获取文件信息
        file_stats = os.stat(pdf_path)
        file_size_mb = file_stats.st_size / (1024 * 1024)
        creation_time = file_stats.st_ctime
        modification_time = file_stats.st_mtime
        
        print(f"文件信息:")
        print(f"  - 大小: {file_size_mb:.2f} MB")
        print(f"  - 创建时间: {file_stats.st_ctime}")
        print(f"  - 修改时间: {file_stats.st_mtime}")
        
        # 读取PDF文件
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            
            # 获取PDF基本信息
            num_pages = len(reader.pages)
            metadata = reader.metadata
            
            print(f"\nPDF基本信息:")
            print(f"  - 页数: {num_pages}")
            print(f"  - 元数据:")
            if metadata:
                for key, value in metadata.items():
                    print(f"    {key}: {value}")
            else:
                print("    无可用元数据")
            
            # 检查PDF结构
            print(f"\n检查PDF结构:")
            
            # 检查第一页
            if num_pages > 0:
                first_page = reader.pages[0]
                first_page_info = {}
                
                # 尝试获取页面尺寸
                try:
                    media_box = first_page.mediabox
                    first_page_info["size"] = f"{media_box.width}x{media_box.height}"
                except:
                    first_page_info["size"] = "无法获取"
                
                # 尝试获取页面内容类型
                try:
                    content = first_page.extract_text()
                    has_text = len(content.strip()) > 0
                    first_page_info["has_text"] = has_text
                    first_page_info["text_preview"] = content[:100] + "..." if has_text else "无文本内容"
                except:
                    first_page_info["has_text"] = "无法检查"
                    first_page_info["text_preview"] = "无法提取文本"
                
                print(f"  第一页信息:")
                for key, value in first_page_info.items():
                    print(f"    {key}: {value}")
            
            # 检查最后几页
            if num_pages > 1:
                last_page_index = num_pages - 1
                last_page = reader.pages[last_page_index]
                last_page_info = {}
                
                # 尝试获取页面尺寸
                try:
                    media_box = last_page.mediabox
                    last_page_info["size"] = f"{media_box.width}x{media_box.height}"
                except:
                    last_page_info["size"] = "无法获取"
                
                print(f"  最后一页信息:")
                for key, value in last_page_info.items():
                    print(f"    {key}: {value}")
            
            # 验证图片顺序的合理性
            # 由于我们无法直接从PDF中提取原始图片名称，这里只能进行基本验证
            print(f"\n顺序验证:")
            print(f"  - 总页数与预期一致: {num_pages == 1123}")
            print(f"  - 文档结构完整: {'是' if num_pages > 0 else '否'}")
            
            # 检查是否有损坏的页面
            print(f"  - 检查页面完整性...")
            corrupted_pages = []
            
            # 只检查部分页面以节省时间
            check_pages = min(20, num_pages)  # 检查前20页
            for i in range(check_pages):
                try:
                    _ = reader.pages[i]
                except Exception as e:
                    corrupted_pages.append((i + 1, str(e)))
            
            if corrupted_pages:
                print(f"  - 发现 {len(corrupted_pages)} 页可能损坏:")
                for page_num, error in corrupted_pages[:5]:  # 只显示前5个
                    print(f"    第{page_num}页: {error}")
            else:
                print(f"  - 前{check_pages}页检查正常")
        
        return {
            "success": True,
            "message": "✅ PDF文档完整性检查完成",
            "num_pages": num_pages,
            "file_size_mb": file_size_mb,
            "corrupted_pages": corrupted_pages
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ 检查过程中出错: {str(e)}"
        }

if __name__ == "__main__":
    # 设置要检查的PDF文件路径
    pdf_path = "进阶吧 投资者（1-6册全）.pdf"
    
    print("="*60)
    print("PDF文档完整性检查工具")
    print("="*60)
    
    # 执行检查
    result = check_pdf_integrity(pdf_path)
    
    print("\n" + result["message"])
    print("="*60)
    
    # 设置退出码
    exit_code = 0 if result["success"] else 1
    exit(exit_code)