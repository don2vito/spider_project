import os
import time
import random
import logging
import pandas as pd
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageDownloader:
    def __init__(self, excel_path, save_dir="雪球图书 - 进阶吧 投资者", max_workers=5):
        self.excel_path = excel_path
        self.save_dir = save_dir
        self.max_workers = max_workers
        
        # 初始化统计信息
        self.total_images = 0
        self.successful_downloads = 0
        self.failed_downloads = 0
        self.failed_urls = []
        
        # 准备保存目录
        self._prepare_save_directory()
    
    def _prepare_save_directory(self):
        """创建保存图片的目录"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            logger.info(f"创建保存目录: {self.save_dir}")
        else:
            logger.info(f"保存目录已存在: {self.save_dir}")
    
    def read_excel_data(self):
        """读取Excel文件中的数据"""
        try:
            logger.info(f"开始读取Excel文件: {self.excel_path}")
            df = pd.read_excel(self.excel_path)
            
            # 验证必要的列是否存在
            if '总的序号' not in df.columns:
                raise ValueError("Excel文件中缺少'总的序号'列")
            if '图片链接' not in df.columns:
                raise ValueError("Excel文件中缺少'图片链接'列")
            
            # 提取需要的数据
            data = df[['总的序号', '图片链接']].copy()
            self.total_images = len(data)
            logger.info(f"成功读取{self.total_images}条图片数据")
            
            return data
        except Exception as e:
            logger.error(f"读取Excel文件时出错: {str(e)}")
            raise
    
    def get_random_user_agent(self):
        """获取随机的User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/88.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        ]
        return random.choice(user_agents)
    
    def get_headers(self, url):
        """生成请求头"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        headers = {
            "User-Agent": self.get_random_user_agent(),
            "Referer": f"https://{domain}/",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        }
        return headers
    
    def download_image(self, index, url):
        """下载单个图片"""
        # 验证URL
        if not url or not isinstance(url, str) or not url.startswith(('http://', 'https://')):
            logger.error(f"序号 {index}: 无效的图片链接")
            self.failed_downloads += 1
            self.failed_urls.append((index, url))
            return False
        
        # 获取文件扩展名
        parsed_url = urlparse(url)
        path = parsed_url.path
        ext = os.path.splitext(path)[1] if os.path.splitext(path)[1] else '.jpg'
        
        # 确保扩展名有效
        if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'
        
        # 生成保存路径
        save_path = os.path.join(self.save_dir, f"{index}{ext}")
        
        # 重试机制
        max_retries = 3
        for retry in range(max_retries):
            try:
                # 设置随机延迟，避免爬取过快
                if retry == 0:
                    time.sleep(random.uniform(0.5, 2.0))
                else:
                    # 指数退避策略
                    backoff_time = 2 ** retry + random.uniform(0, 1)
                    logger.info(f"序号 {index}: 第 {retry+1} 次重试，等待 {backoff_time:.2f} 秒")
                    time.sleep(backoff_time)
                
                # 发送请求
                headers = self.get_headers(url)
                response = requests.get(url, headers=headers, timeout=30, stream=True)
                
                # 检查响应状态
                if response.status_code == 200:
                    # 保存图片
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    
                    logger.info(f"序号 {index}: 成功下载 - {url}")
                    self.successful_downloads += 1
                    return True
                else:
                    logger.warning(f"序号 {index}: 下载失败，HTTP状态码: {response.status_code} - {url}")
                    
                    # 处理特定的状态码
                    if response.status_code == 403:
                        logger.warning("检测到403 Forbidden，可能被反爬机制拦截")
                        # 增加延迟
                        time.sleep(random.uniform(3, 5))
                    elif response.status_code == 429:
                        logger.warning("检测到429 Too Many Requests，请求过于频繁")
                        time.sleep(random.uniform(5, 10))
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"序号 {index}: 请求异常 (重试 {retry+1}/{max_retries}): {str(e)} - {url}")
            except Exception as e:
                logger.error(f"序号 {index}: 未知错误 (重试 {retry+1}/{max_retries}): {str(e)} - {url}")
        
        # 所有重试都失败
        logger.error(f"序号 {index}: 达到最大重试次数，下载失败 - {url}")
        self.failed_downloads += 1
        self.failed_urls.append((index, url))
        return False
    
    def download_all_images(self):
        """下载所有图片"""
        try:
            # 读取数据
            data = self.read_excel_data()
            
            logger.info("开始下载图片...")
            start_time = time.time()
            
            # 使用线程池进行并发下载
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 创建任务
                futures = {executor.submit(self.download_image, row['总的序号'], row['图片链接']): index 
                          for index, row in data.iterrows()}
                
                # 使用进度条显示下载进度
                with tqdm(total=len(futures), desc="下载进度") as pbar:
                    for future in as_completed(futures):
                        pbar.update(1)
                        try:
                            future.result()
                        except Exception as e:
                            logger.error(f"任务执行出错: {str(e)}")
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 生成统计报告
            self.generate_report(elapsed_time)
            
        except Exception as e:
            logger.error(f"下载过程中发生严重错误: {str(e)}")
            raise
    
    def generate_report(self, elapsed_time):
        """生成下载统计报告"""
        logger.info("\n========== 下载统计报告 ==========")
        logger.info(f"总图片数量: {self.total_images}")
        logger.info(f"成功下载: {self.successful_downloads}")
        logger.info(f"下载失败: {self.failed_downloads}")
        logger.info(f"成功率: {self.successful_downloads/self.total_images*100:.2f}%")
        logger.info(f"总耗时: {elapsed_time:.2f} 秒")
        logger.info(f"平均速度: {self.successful_downloads/elapsed_time:.2f} 张/秒")
        
        # 保存失败的URL到文件
        if self.failed_urls:
            with open('failed_downloads.txt', 'w', encoding='utf-8') as f:
                f.write("序号,图片链接\n")
                for index, url in self.failed_urls:
                    f.write(f"{index},{url}\n")
            logger.info(f"失败的图片链接已保存到: failed_downloads.txt")
        
        logger.info("================================")

def main():
    """主函数"""
    try:
        # Excel文件路径
        excel_path = r'd:/project/雪球爬虫项目/1. 图片链接拆分多行.xlsx'
        
        # 创建下载器实例
        downloader = ImageDownloader(
            excel_path=excel_path,
            save_dir="雪球图书 - 进阶吧 投资者",
            max_workers=5  # 可以根据需要调整并发数
        )
        
        # 开始下载
        downloader.download_all_images()
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()