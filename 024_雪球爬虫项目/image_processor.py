import os
import re
from natsort import natsorted

class ImageProcessor:
    def __init__(self, image_folder):
        self.image_folder = image_folder
        self.supported_formats = ['.jpg', '.jpeg', '.png']
        
    def get_sorted_images(self):
        """获取按自然数字顺序排序的图片文件列表"""
        # 获取所有图片文件
        image_files = []
        for file in os.listdir(self.image_folder):
            if os.path.isfile(os.path.join(self.image_folder, file)):
                # 检查文件扩展名是否在支持的格式中
                ext = os.path.splitext(file)[1].lower()
                if ext in self.supported_formats:
                    image_files.append(file)
        
        # 使用自然排序（按数字顺序而不是字典序）
        sorted_images = natsorted(image_files)
        
        # 返回完整路径
        return [os.path.join(self.image_folder, img) for img in sorted_images]
    
    def validate_images(self, image_paths):
        """验证所有图片文件是否存在且可读"""
        valid_images = []
        invalid_images = []
        print(f"开始验证 {len(image_paths)} 张图片...")
        
        for i, img_path in enumerate(image_paths, 1):
            try:
                # 确保img_path是字符串类型
                if not isinstance(img_path, str):
                    invalid_images.append((img_path, f"路径类型错误: {type(img_path)}"))
                    continue
                    
                # 检查文件是否存在且是文件
                if not os.path.exists(img_path) or not os.path.isfile(img_path):
                    invalid_images.append((img_path, "文件不存在或不是文件"))
                    continue
                    
                # 检查是否可读
                with open(img_path, 'rb') as f:
                    # 读取一小部分进行测试
                    _ = f.read(4)
                valid_images.append(img_path)
                
                # 打印进度信息
                if i % 100 == 0 or i == len(image_paths):
                    print(f"验证进度: {i}/{len(image_paths)} 张，已验证通过: {len(valid_images)} 张")
                    
            except Exception as e:
                invalid_images.append((img_path, str(e)))
        
        print(f"图片验证完成: {len(valid_images)}/{len(image_paths)} 张图片验证通过")
        return valid_images, invalid_images

# 测试代码
if __name__ == "__main__":
    image_folder = "d:\project\雪球爬虫项目\雪球图书 - 进阶吧 投资者"
    processor = ImageProcessor(image_folder)
    
    print("正在获取排序后的图片列表...")
    sorted_images = processor.get_sorted_images()
    print(f"找到 {len(sorted_images)} 张图片")
    
    # 显示前10张和后10张图片作为示例
    if sorted_images:
        print("\n前10张图片:")
        for img in sorted_images[:10]:
            print(f"  - {os.path.basename(img)}")
        
        if len(sorted_images) > 10:
            print("\n后10张图片:")
            for img in sorted_images[-10:]:
                print(f"  - {os.path.basename(img)}")
    
    # 验证图片
    print("\n正在验证图片文件...")
    valid_images, invalid_images = processor.validate_images(sorted_images)
    
    print(f"有效图片: {len(valid_images)}")
    if invalid_images:
        print(f"无效图片: {len(invalid_images)}")
        for img, error in invalid_images[:5]:  # 只显示前5个错误
            print(f"  - {os.path.basename(img)}: {error}")
        if len(invalid_images) > 5:
            print(f"  ... 还有 {len(invalid_images) - 5} 个错误未显示")