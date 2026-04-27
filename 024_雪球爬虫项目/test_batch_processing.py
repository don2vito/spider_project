import os
import sys
import gc
from image_processor import ImageProcessor
from pdf_generator import PDFGenerator

def test_batch_processing():
    """
    测试分批次处理功能，只处理前50张图片
    """
    print("开始测试函数...")
    
    # 设置图片目录路径
    image_dir = "d:/project/雪球爬虫项目/雪球图书 - 进阶吧 投资者/"
    print(f"使用图片目录: {image_dir}")
    
    # 验证目录是否存在
    if not os.path.exists(image_dir):
        print(f"错误: 图片目录不存在 - {image_dir}")
        return False
    
    # 设置输出PDF路径
    output_pdf_path = "测试_小批量.pdf"  # 使用更简单的文件名
    print(f"输出PDF路径: {output_pdf_path}")
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_pdf_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 创建图片处理器实例
    print("创建ImageProcessor实例...")
    processor = ImageProcessor(image_folder=image_dir)
    
    # 获取所有图片文件并排序
    print("获取图片文件列表...")
    all_files = processor.get_sorted_images()  # 使用ImageProcessor的正确方法名
    
    if not all_files:
        print("错误: 没有找到图片文件")
        return False
    
    # 只取前50张图片用于测试
    test_images = all_files[:50]
    print(f"找到了 {len(all_files)} 张图片，使用前 {len(test_images)} 张进行测试")
    
    # 打印前几张图片名称作为参考
    print("前5张图片:")
    for i, img_path in enumerate(test_images[:5]):
        print(f"  {i+1}: {os.path.basename(img_path)}")
    
    # 设置批次大小
    batch_size = 20
    total_batches = (len(test_images) + batch_size - 1) // batch_size
    print(f"\n总共需要处理 {len(test_images)} 张图片，将分 {total_batches} 批次处理，每批 {batch_size} 张")
    
    # 创建临时PDF文件用于合并
    temp_pdfs = []
    success = False
    
    try:
        # 分批处理图片
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(test_images))
            batch_images = test_images[start_idx:end_idx]
            
            print(f"\n开始处理第 {batch_idx + 1}/{total_batches} 批次，包含图片 {start_idx + 1}-{end_idx}")
            
            # 为每个批次创建临时PDF
            temp_pdf_path = f"temp_test_batch_{batch_idx}.pdf"
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
            else:
                success = False
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
        else:
            # 没有成功生成的临时PDF
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
    
    # 验证生成的PDF
    if success and os.path.exists(output_pdf_path):
        file_size = os.path.getsize(output_pdf_path) / 1024  # KB
        print(f"\n测试PDF文件已成功生成！")
        print(f"文件路径: {output_pdf_path}")
        print(f"文件大小: {file_size:.2f} KB")
        print("建议手动验证PDF文件的页面数量和内容")
    else:
        print("\n测试失败，未能生成PDF文件")
    
    return success

if __name__ == "__main__":
    # 启用垃圾回收
    gc.enable()
    print("开始测试分批次处理功能...")
    result = test_batch_processing()
    sys.exit(0 if result else 1)