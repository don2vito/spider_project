"""
PDF 生成模块
负责下载报告图片并转换为 PDF 文件
"""

import re
import os
import time
import logging
import tempfile

import requests
import img2pdf

from scraper import _session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 图片下载请求头
IMAGE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://www.cbndata.com/",
}


def download_image(url, save_path, timeout=(10, 60)):
    """
    下载单张图片，支持重试。

    Args:
        url: 图片 URL
        save_path: 保存路径
        timeout: 连接和读取超时时间（秒）

    Returns:
        bool: 是否下载成功
    """
    for attempt in range(3):
        try:
            resp = _session.get(url, timeout=timeout, stream=True, headers=IMAGE_HEADERS)

            if resp.status_code == 403:
                logger.warning(f"图片下载被拒绝 (403)，可能是 token 过期: {url[:80]}...")
                return False

            resp.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # 验证文件大小
            file_size = os.path.getsize(save_path)
            if file_size < 1024:  # 小于 1KB 可能是错误页面
                logger.warning(f"下载的图片文件过小 ({file_size} bytes): {url[:80]}...")
                os.remove(save_path)
                return False

            return True

        except requests.RequestException as e:
            logger.warning(f"图片下载失败 (尝试 {attempt + 1}/3): {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)  # 指数退避：1s, 2s

    return False


def generate_pdf(image_urls, title, progress_callback=None):
    """
    将图片 URL 列表转换为 PDF 文件。

    Args:
        image_urls: 图片 URL 列表（按页码顺序）
        title: 报告标题（用于 PDF 文件名）
        progress_callback: 进度回调函数 callback(current, total, message)

    Returns:
        tuple: (pdf_bytes, filename)
    """
    total = len(image_urls)
    if total == 0:
        raise ValueError("图片 URL 列表为空，无法生成 PDF")

    logger.info(f"开始生成 PDF: '{title}'，共 {total} 页")

    with tempfile.TemporaryDirectory() as tmpdir:
        image_paths = []
        success_count = 0
        fail_count = 0

        for i, url in enumerate(image_urls, 1):
            ext = ".jpg"
            save_path = os.path.join(tmpdir, f"{i:03d}{ext}")

            if progress_callback:
                progress_callback(i, total, f"正在下载第 {i}/{total} 页...")

            success = download_image(url, save_path)

            if success:
                image_paths.append(save_path)
                success_count += 1
            else:
                fail_count += 1
                logger.warning(f"第 {i} 页下载失败，跳过")

        if not image_paths:
            raise ValueError("所有图片下载均失败，无法生成 PDF")

        if fail_count > 0:
            logger.warning(f"共 {fail_count} 页下载失败，将使用 {success_count} 页生成 PDF")

        if progress_callback:
            progress_callback(total, total, "正在生成 PDF 文件...")

        # 使用 img2pdf 无损转换（JPEG 直接嵌入 PDF，不重编码）
        pdf_bytes = img2pdf.convert(image_paths)

        # 清理文件名中的非法字符
        safe_title = re.sub(r'[\\/:*?"<>|\r\n]', '_', title).strip()
        safe_title = re.sub(r'_+', '_', safe_title)  # 合并连续下划线
        filename = f"{safe_title}.pdf"

        logger.info(f"PDF 生成完成: {filename} ({len(pdf_bytes) / 1024:.1f} KB, {success_count} 页)")

        return pdf_bytes, filename
