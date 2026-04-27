import os
import sys
import gc
from PIL import Image
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

class PDFGenerator:
    def __init__(self, output_pdf_path):
        # 确保路径正确，特别是在Windows系统中
        self.output_pdf_path = os.path.normpath(output_pdf_path)
        # 确保输出目录存在
        output_dir = os.path.dirname(self.output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    
    def image_to_pdf(self, image_paths):
        """
        将图片列表转换为PDF文档
        
        Args:
            image_paths: 图片文件路径列表
        
        Returns:
            bool: 转换是否成功
        """
        try:
            print(f"开始生成PDF: {self.output_pdf_path}")
            
            # 过滤有效图片路径（确保只有图片格式）
            valid_image_paths = []
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif'}
            
            for img_path in image_paths:
                if isinstance(img_path, str) and os.path.exists(img_path) and os.path.isfile(img_path):
                    # 检查文件扩展名是否为图片格式
                    ext = os.path.splitext(img_path)[1].lower()
                    if ext in image_extensions:
                        valid_image_paths.append(img_path)
            
            print(f"总共需要处理 {len(image_paths)} 张图片")
            print(f"过滤后有效图片: {len(valid_image_paths)} 张")
            
            if not valid_image_paths:
                print("错误: 没有有效的图片可以处理")
                return False
            
            # 创建PDF画布
            print("创建PDF画布...")
            
            # 使用A4作为默认页面大小开始
            c = canvas.Canvas(self.output_pdf_path, pagesize=A4)
            
            success_count = 0
            error_count = 0
            
            # 每处理一定数量的图片后进行垃圾回收
            gc_interval = 50
            
            for i, image_path in enumerate(valid_image_paths):
                try:
                    # 定期进行垃圾回收，避免内存占用过高
                    if (i + 1) % gc_interval == 0:
                        print(f"执行垃圾回收，已处理 {i+1} 张图片...")
                        gc.collect()
                    
                    # 确保路径正确
                    image_path = os.path.normpath(image_path)
                    
                    # 显示进度信息，但避免输出过多
                    if (i + 1) % 10 == 0 or i == len(valid_image_paths) - 1:
                        print(f"处理进度: {i+1}/{len(valid_image_paths)} 张图片")
                    
                    # 打开图片并获取尺寸
                    with Image.open(image_path) as img:
                        # 转换RGBA为RGB（PDF不支持RGBA）
                        if img.mode == 'RGBA':
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
                            img = background
                        
                        # 获取图片尺寸
                        img_width, img_height = img.size
                        
                        # 对于非常大的图片，可以进行适当的缩放以避免内存问题
                        max_dimension = 5000  # 最大像素维度
                        scale = 1.0
                        if img_width > max_dimension or img_height > max_dimension:
                            scale = max_dimension / max(img_width, img_height)
                            img_width = int(img_width * scale)
                            img_height = int(img_height * scale)
                            
                        # 转换像素为点（1英寸=72点），假设图片DPI为150
                        dpi = 150
                        width_in_points = (img_width / dpi) * 72
                        height_in_points = (img_height / dpi) * 72
                        
                        # 确保页面尺寸精确适应图片比例
                        c.setPageSize((width_in_points, height_in_points))
                        
                        # 图片将占据整个页面
                        x_pos = 0
                        y_pos = 0
                        
                        # 使用drawImage添加图片，启用preserveAspectRatio
                        c.drawImage(image_path, x_pos, y_pos, width=width_in_points, height=height_in_points, preserveAspectRatio=True)
                        
                        # 完成当前页并添加新页（最后一页不需要添加新页）
                        if i < len(valid_image_paths) - 1:
                            c.showPage()
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"处理图片 {os.path.basename(image_path)} 时出错: {str(e)}")
                    error_count += 1
                    continue
            
            # 保存PDF
            print(f"保存PDF文档，成功处理 {success_count} 张图片...")
            c.save()
            
            # 验证文件是否创建并包含内容
            if os.path.exists(self.output_pdf_path):
                file_size = os.path.getsize(self.output_pdf_path)
                print(f"PDF文档已成功生成: {self.output_pdf_path}")
                print(f"PDF文件大小: {file_size/1024/1024:.2f} MB")
                return True
            else:
                print("警告: PDF文件可能未创建")
                return False
                
        except Exception as e:
            print(f"生成PDF时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# 测试代码
if __name__ == "__main__":
    from image_processor import ImageProcessor
    
    # 使用原始字符串来避免路径转义问题
    image_folder = r"d:\project\雪球爬虫项目\雪球图书 - 进阶吧 投资者"
    test_output = r"d:\project\雪球爬虫项目\test_output.pdf"
    
    print(f"测试图片文件夹: {image_folder}")
    print(f"测试输出PDF: {test_output}")
    
    # 获取排序后的图片
    processor = ImageProcessor(image_folder)
    sorted_images = processor.get_sorted_images()
    
    # 只使用前10张图片进行测试
    test_images = sorted_images[:10]
    print(f"使用 {len(test_images)} 张图片进行测试")
    for i, img_path in enumerate(test_images[:3]):
        print(f"  示例图片 {i+1}: {os.path.basename(img_path)}")
    
    # 生成测试PDF
    generator = PDFGenerator(test_output)
    success = generator.image_to_pdf(test_images)
    
    # 检查文件是否实际创建
    if success and os.path.exists(test_output):
        file_size = os.path.getsize(test_output) / 1024 / 1024  # MB
        print(f"测试PDF生成成功: {test_output}")
        print(f"PDF文件大小: {file_size:.2f} MB")
    else:
        print("测试PDF生成失败")
        if os.path.exists(test_output):
            print(f"  但文件已创建: {test_output}")
        else:
            print(f"  文件未创建: {test_output}")