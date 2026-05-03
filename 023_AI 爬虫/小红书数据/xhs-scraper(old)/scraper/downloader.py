"""
Media downloader for Xiaohongshu images and videos.
Handles URL expiration (30s) with immediate download strategy.
"""
import os
import time
import logging
import requests as http_requests

logger = logging.getLogger(__name__)

# Default headers for media downloads
MEDIA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.xiaohongshu.com/",
}


class MediaDownloader:
    """Downloads images and videos from Xiaohongshu CDN."""

    def __init__(self, timeout_img=15, timeout_video=120, retry=3):
        self.timeout_img = timeout_img
        self.timeout_video = timeout_video
        self.retry = retry

    def download_image(self, url: str) -> bytes:
        """Download a single image, return bytes."""
        for attempt in range(self.retry):
            try:
                resp = http_requests.get(
                    url,
                    headers=MEDIA_HEADERS,
                    timeout=self.timeout_img,
                    stream=True,
                )
                if resp.status_code == 200:
                    return resp.content
                elif resp.status_code == 403:
                    logger.warning(f"Image URL expired (403): {url[:80]}...")
                    return b""
                else:
                    logger.warning(f"Image download failed: HTTP {resp.status_code}")
            except Exception as e:
                logger.warning(f"Image download attempt {attempt + 1} failed: {e}")
            if attempt < self.retry - 1:
                time.sleep(0.5)

        return b""

    def download_images(self, urls: list) -> list[bytes]:
        """Download multiple images, return list of bytes."""
        results = []
        for i, url in enumerate(urls):
            if not url:
                results.append(b"")
                continue
            data = self.download_image(url)
            results.append(data)
            if i < len(urls) - 1:
                time.sleep(0.3)  # Rate limit between downloads
        return results

    def download_video(self, url: str) -> bytes:
        """Download a video, return bytes."""
        for attempt in range(self.retry):
            try:
                resp = http_requests.get(
                    url,
                    headers=MEDIA_HEADERS,
                    timeout=self.timeout_video,
                    stream=True,
                )
                if resp.status_code == 200:
                    chunks = []
                    for chunk in resp.iter_content(chunk_size=8192):
                        chunks.append(chunk)
                    return b"".join(chunks)
                elif resp.status_code == 403:
                    logger.warning(f"Video URL expired (403): {url[:80]}...")
                    return b""
                else:
                    logger.warning(f"Video download failed: HTTP {resp.status_code}")
            except Exception as e:
                logger.warning(f"Video download attempt {attempt + 1} failed: {e}")
            if attempt < self.retry - 1:
                time.sleep(1)

        return b""
