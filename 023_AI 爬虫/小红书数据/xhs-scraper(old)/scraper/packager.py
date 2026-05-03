"""
ZIP packager for Xiaohongshu notes.
Packages note metadata, content, images, videos, and comments into a ZIP file.
"""
import json
import io
import time
import zipfile
import logging
from datetime import datetime
from typing import Optional

from scraper.downloader import MediaDownloader

logger = logging.getLogger(__name__)


class NotePackager:
    """Packages a single note's data and media into a ZIP byte stream."""

    def __init__(self, downloader: Optional[MediaDownloader] = None):
        self.downloader = downloader or MediaDownloader()

    def _safe_filename(self, name: str, max_len: int = 50) -> str:
        """Clean a string to be used as a filename."""
        # Remove illegal characters
        safe = "".join(c for c in name if c not in r'<>:"/\|?*')
        # Trim to max length
        return safe.strip()[:max_len] or "untitled"

    def _format_timestamp(self, ts_ms: int) -> str:
        """Convert millisecond timestamp to readable string."""
        if not ts_ms:
            return ""
        try:
            return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(ts_ms)

    def package_note(self, note_detail: dict, comments: list = None) -> bytes:
        """
        Package a note into a ZIP byte stream.

        ZIP structure:
          {title}/
          ├── note_info.json    (metadata)
          ├── content.txt       (full text content)
          ├── images/
          │   ├── image_1.jpg
          │   ├── image_2.jpg
          │   └── ...
          ├── video.mp4         (if video note)
          └── comments.json     (all comments and replies)
        """
        buf = io.BytesIO()
        note_id = note_detail.get("note_id", "unknown")
        title = note_detail.get("title", "") or note_id
        folder = self._safe_filename(title)

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Metadata JSON
            interact = note_detail.get("interact_info", {})
            user = note_detail.get("user", {})
            meta = {
                "note_id": note_id,
                "title": title,
                "type": note_detail.get("type", "normal"),
                "author": user.get("nickname", ""),
                "author_id": user.get("user_id", ""),
                "publish_time": self._format_timestamp(note_detail.get("time", 0)),
                "last_update_time": self._format_timestamp(note_detail.get("last_update_time", 0)),
                "likes": interact.get("liked_count", "0"),
                "favorites": interact.get("collected_count", "0"),
                "comments_count": interact.get("comment_count", "0"),
                "shares": interact.get("share_count", "0"),
                "tags": [t.get("name", "") for t in note_detail.get("tag_list", [])],
                "link": f"https://www.xiaohongshu.com/explore/{note_id}",
            }
            zf.writestr(
                f"{folder}/note_info.json",
                json.dumps(meta, ensure_ascii=False, indent=2),
            )

            # 2. Full text content
            desc = note_detail.get("desc", "")
            if desc:
                zf.writestr(f"{folder}/content.txt", desc)

            # 3. Download and save images
            img_urls = note_detail.get("extracted_img_urls", [])
            if img_urls:
                logger.info(f"Downloading {len(img_urls)} images for note {note_id}...")
                images_data = self.downloader.download_images(img_urls)
                for i, img_data in enumerate(images_data):
                    if img_data:
                        ext = ".jpg"
                        if i < len(img_urls):
                            url_lower = img_urls[i].lower()
                            if ".png" in url_lower:
                                ext = ".png"
                            elif ".webp" in url_lower:
                                ext = ".webp"
                        zf.writestr(f"{folder}/images/image_{i + 1}{ext}", img_data)
                        logger.info(f"  Saved image_{i + 1}{ext} ({len(img_data)} bytes)")

            # 4. Download and save video
            video_url = note_detail.get("extracted_video_url", "")
            if video_url:
                logger.info(f"Downloading video for note {note_id}...")
                video_data = self.downloader.download_video(video_url)
                if video_data:
                    zf.writestr(f"{folder}/video.mp4", video_data)
                    logger.info(f"  Saved video.mp4 ({len(video_data)} bytes)")

            # 5. Save comments
            if comments:
                # Format comments for JSON export
                formatted_comments = self._format_comments(comments)
                zf.writestr(
                    f"{folder}/comments.json",
                    json.dumps(formatted_comments, ensure_ascii=False, indent=2),
                )

                # Also save as readable text
                comments_text = self._comments_to_text(formatted_comments)
                if comments_text:
                    zf.writestr(f"{folder}/comments.txt", comments_text)

        buf.seek(0)
        zip_size = len(buf.getvalue())
        logger.info(f"Packaged note '{title}' -> {zip_size} bytes")
        return buf.getvalue()

    def _format_comments(self, comments: list) -> list:
        """Recursively format comments for JSON export."""
        formatted = []
        for c in comments:
            user_info = c.get("user_info", c.get("user", {}))
            fc = {
                "id": c.get("id", ""),
                "content": c.get("content", ""),
                "author": user_info.get("nickname", ""),
                "author_id": user_info.get("user_id", ""),
                "publish_time": self._format_timestamp(c.get("create_time", 0)),
                "ip_location": c.get("ip_location", ""),
                "likes": c.get("like_count", "0"),
            }

            # Handle sub-comments
            sub_comments = c.get("sub_comments", [])
            if sub_comments:
                fc["replies"] = self._format_comments(sub_comments)

            formatted.append(fc)
        return formatted

    def _comments_to_text(self, comments: list, indent: int = 0) -> str:
        """Convert comments to readable text format."""
        lines = []
        prefix = "  " * indent
        for c in comments:
            author = c.get("author", "Anonymous")
            content = c.get("content", "")
            time_str = c.get("publish_time", "")
            ip = c.get("ip_location", "")
            likes = c.get("likes", "0")

            line = f"{prefix}[{author}] ({time_str}"
            if ip:
                line += f" · {ip}"
            line += f") ❤️ {likes}\n{prefix}  {content}"
            lines.append(line)

            replies = c.get("replies", [])
            if replies:
                lines.append("")
                lines.append(self._comments_to_text(replies, indent + 1))

            lines.append("")

        return "\n".join(lines)
