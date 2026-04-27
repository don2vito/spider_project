#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序：将图片文件夹中的所有图片按字母数字顺序合并为PDF文档
"""

import os
import sys
import time
import gc
from datetime import datetime

# 导入之前开发的模块
from image_processor import ImageProcessor
from pdf_generator import PDFGenerator

def main():
    """主函数，协调整个图片转PDF的过程"""
    print("="*80)
    print("图片转PDF合并工具")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 配置参数
    image_folder = r"d:\project\雪球爬虫项目\雪球图书 - 进阶吧 投资者"
    output_pdf_path = os.path.join(os.getcwd(), "进阶吧 投资者（1-6册全）.pdf")
    
    print(f"图片文件夹: {image_folder}")
    print(f"输出PDF文件: {output_pdf_path}")
    print("-"*80)
    
    # 1. 检查图片文件夹是否存在
    if not os.path.exists(image_folder):
        print(f"错误: 图片文件夹不存在 - {image_folder}")
        return False
    
    # 2. 初始化图片处理器并获取排序后的图片列表
    start_time = time.time()
    print("正在获取并排序图片...")
    
    try:
        processor = ImageProcessor(image_folder)
        sorted_images = processor.get_sorted_images()
        
        if not sorted_images:
            print("错误: 未找到有效的图片文件")
            return False
        
        # 验证图片
        valid_images, invalid_images = processor.validate_images(sorted_images)
        
        if invalid_images:
            print(f"警告: 有 {len(invalid_images)} 张图片验证失败，已跳过")
            # 可以选择只显示前5个失败的图片信息
            if len(invalid_images) <= 5:
                for img_path, error in invalid_images:
                    print(f"  - {os.path.basename(str(img_path))}: {error}")
            else:
                for img_path, error in invalid_images[:3]:
                    print(f"  - {os.path.basename(str(img_path))}: {error}")
                print(f"  - ... 还有 {len(invalid_images) - 3} 个错误未显示")
        
        if not valid_images:
            print("错误: 没有有效的图片可以处理")
            return False
        
        # 显示统计信息
        print(f"找到并成功排序 {len(sorted_images)} 张图片")
        print(f"验证通过的图片数量: {len(valid_images)}")
        
        # 处理所有验证通过的图片
        print(f"准备处理 {len(valid_images)} 张图片")
        print(f"排序用时: {time.time() - start_time:.2f} 秒")
        # 安全地获取文件名
        first_5_names = []
        for img in valid_images[:5]:
            if isinstance(img, str):
                first_5_names.append(os.path.basename(img))
        
        last_5_names = []
        for img in valid_images[-5:]:
            if isinstance(img, str):
                last_5_names.append(os.path.basename(img))
        
        print(f"前5张图片: {', '.join(first_5_names)}")
        print(f"后5张图片: {', '.join(last_5_names)}")
        print("-"*80)
        
    except Exception as e:
        print(f"错误: 获取或排序图片时出错 - {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 初始化PDF生成器并分批处理图片
    print(f"开始生成PDF文档...")
    start_time = time.time()
    success = False
    temp_pdfs = []
    
    try:
        # 为了避免内存问题，使用分批处理方式
        batch_size = 100
        total_batches = (len(valid_images) + batch_size - 1) // batch_size
        print(f"总共需要处理 {len(valid_images)} 张图片，将分 {total_batches} 批次处理，每批 {batch_size} 张")
        
        # 分批处理图片
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(valid_images))
            batch_images = valid_images[start_idx:end_idx]
            
            print(f"\n开始处理第 {batch_idx + 1}/{total_batches} 批次，包含图片 {start_idx + 1}-{end_idx}")
            
            # 为每个批次创建临时PDF
            temp_pdf_path = f"temp_batch_{batch_idx}.pdf"
            temp_pdf_generator = PDFGenerator(temp_pdf_path)
            
            # 处理当前批次的图片
            batch_success = temp_pdf_generator.image_to_pdf(batch_images)
            
            if batch_success and os.path.exists(temp_pdf_path):
                temp_pdfs.append(temp_pdf_path)
                print(f"批次 {batch_idx + 1} 处理成功")
            else:
                print(f"批次 {batch_idx + 1} 处理失败")
                
            # 执行垃圾回收
            gc.collect()
        
        # 如果只有一个批次，直接重命名为最终PDF
        if len(temp_pdfs) == 1:
            if os.path.exists(temp_pdfs[0]):
                # 先删除可能存在的目标文件
                if os.path.exists(output_pdf_path):
                    os.remove(output_pdf_path)
                # 重命名临时文件为最终文件
                os.rename(temp_pdfs[0], output_pdf_path)
                success = True
                print(f"直接使用单个批次的结果作为最终PDF")
        elif len(temp_pdfs) > 1:
            # 如果有多个批次，需要合并PDFs
            print(f"\n合并 {len(temp_pdfs)} 个临时PDF文件...")
            try:
                # 使用PyPDF2合并PDFs
                from PyPDF2 import PdfWriter, PdfReader
                
                merger = PdfWriter()
                
                for pdf in temp_pdfs:
                    if os.path.exists(pdf):
                        print(f"添加文件: {pdf}")
                        merger.append(pdf)
                
                # 写入合并后的PDF
                merger.write(output_pdf_path)
                merger.close()
                success = True
                print("PDF文件合并成功")
            except Exception as e:
                print(f"合并PDF时出错: {str(e)}")
                success = False
    
    except Exception as e:
        print(f"生成PDF过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        success = False
    
    finally:
        # 清理临时文件
        print("\n清理临时文件...")
        for pdf in temp_pdfs:
            if os.path.exists(pdf):
                try:
                    os.remove(pdf)
                except:
                    pass
        
        if success and os.path.exists(output_pdf_path):
            # 计算文件大小和处理时间
            file_size = os.path.getsize(output_pdf_path) / 1024 / 1024  # MB
            process_time = time.time() - start_time
            
            print("="*80)
            print(f"✅ PDF生成成功！")
            print(f"输出文件: {output_pdf_path}")
            print(f"文件大小: {file_size:.2f} MB")
            print(f"处理时间: {process_time:.2f} 秒")
            print(f"平均处理速度: {len(valid_images)/process_time:.2f} 张/秒")
            print("="*80)
            return True
        else:
            print("❌ PDF生成失败")
            if os.path.exists(output_pdf_path):
                print(f"  但文件已创建，可能不完整: {output_pdf_path}")
                print(f"  文件大小: {os.path.getsize(output_pdf_path)/1024:.2f} KB")
            return False

if __name__ == "__main__":
    # 导入gc模块用于垃圾回收
    import gc
    gc.enable()
    # 运行主程序并设置退出码
    success = main()
    sys.exit(0 if success else 1)