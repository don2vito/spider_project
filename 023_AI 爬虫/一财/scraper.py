"""
CBNData 网站抓取逻辑模块
负责获取免费报告列表和报告详情页图片 URL
"""

import re
import json
import logging
from datetime import datetime

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 请求头配置 - 必须携带 Referer，否则 API 可能拒绝请求
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.cbndata.com/report",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 使用 Session 复用连接
_session = requests.Session()
_session.headers.update(HEADERS)

# API 基础 URL
LIST_API_URL = "https://www.cbndata.com/api/v2/report_products"
DETAIL_PAGE_URL = "https://www.cbndata.com/report/{product_id}/detail"


def get_free_reports(year=None):
    """
    获取指定年度的所有免费报告列表。

    Args:
        year: 目标年份，默认为当前年份

    Returns:
        list[dict]: 报告列表，每项包含 id, title, date, thumbnail_url,
                    images_count, tags, detail_url
    """
    if year is None:
        year = datetime.now().year

    reports = []
    page = 1
    per_page = 12
    should_stop = False

    while not should_stop:
        params = {
            "tags[]": "all",
            "price_category": "price_free",
            "page": page,
            "per": per_page,
        }

        logger.info(f"正在获取第 {page} 页报告数据...")

        try:
            resp = _session.get(LIST_API_URL, params=params, timeout=(10, 30))
            resp.raise_for_status()
            result = resp.json()
        except requests.RequestException as e:
            logger.error(f"获取第 {page} 页失败: {e}")
            break

        data = result.get("data", [])
        meta = result.get("meta", {})

        if not data:
            logger.info("没有更多数据，停止翻页")
            break

        for item in data:
            # 解析日期
            date_str = item.get("date", "")
            try:
                report_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                report_year = report_date.year
            except (ValueError, TypeError):
                continue

            # 如果报告年份早于目标年份，停止遍历
            if report_year < year:
                should_stop = True
                break

            # 仅保留目标年份的报告
            if report_year == year:
                report_info = item.get("report", {})
                tags = [tag.get("name", "") for tag in item.get("tags", []) if tag.get("name")]

                reports.append({
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "date": report_date.strftime("%Y-%m-%d"),
                    "thumbnail_url": item.get("thumbnail_url", ""),
                    "images_count": report_info.get("images_count", 0),
                    "tags": tags,
                    "detail_url": DETAIL_PAGE_URL.format(product_id=item.get("id")),
                })

        # 检查是否还有下一页
        total_pages = meta.get("total_page", 1)
        if page >= total_pages:
            logger.info(f"已到达最后一页 (共 {total_pages} 页)")
            break

        page += 1

    logger.info(f"共获取 {year} 年免费报告 {len(reports)} 份")
    return reports


def _safe_json_parse(raw_str):
    """
    安全解析可能不规范的 JSON 字符串。
    处理 undefined 值、尾部逗号等非标准 JSON 格式。
    """
    cleaned = raw_str.strip()
    # 替换 undefined 为 null
    cleaned = re.sub(r'\bundefined\b', 'null', cleaned)
    # 移除尾部逗号 (如 }, ] 前的逗号)
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 备选：尝试使用 json5
    try:
        import json5
        return json5.loads(cleaned)
    except ImportError:
        pass

    raise ValueError("JSON 解析失败，请检查数据格式")


def get_report_images(product_id):
    """
    获取指定报告的详情页图片 URL 列表。

    每次调用都会重新请求详情页，获取最新的带 token 图片 URL。

    Args:
        product_id: 报告产品 ID

    Returns:
        dict: 包含 product_id, title, images_count, image_urls
    """
    url = DETAIL_PAGE_URL.format(product_id=product_id)
    logger.info(f"正在获取报告 {product_id} 的详情页...")

    try:
        resp = _session.get(url, timeout=(10, 30))
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as e:
        logger.error(f"获取报告 {product_id} 详情页失败: {e}")
        raise

    # 从 HTML 中提取 __INITIAL_STATE__
    pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});\s*</script>'
    match = re.search(pattern, html, re.DOTALL)

    if not match:
        # 尝试更宽松的匹配
        pattern2 = r'__INITIAL_STATE__\s*=\s*({.+?})\s*;?\s*</script>'
        match = re.search(pattern2, html, re.DOTALL)

    if not match:
        raise ValueError(f"未在报告 {product_id} 详情页中找到 __INITIAL_STATE__ 数据")

    raw_json = match.group(1)
    state = _safe_json_parse(raw_json)

    # 提取关键字段
    title = state.get("title", f"报告_{product_id}")
    report = state.get("report", {})
    images_count = report.get("images_count", 0)
    image_urls = report.get("watermark_image_urls", [])

    # 如果 watermark_image_urls 为空，尝试备选字段
    if not image_urls:
        # 尝试从 images 或 pages 字段获取
        image_urls = report.get("images", [])
        if not image_urls:
            image_urls = report.get("pages", [])

    if not image_urls:
        raise ValueError(f"报告 {product_id} 未找到图片 URL")

    logger.info(f"报告 '{title}' 共 {len(image_urls)} 页图片")

    return {
        "product_id": product_id,
        "title": title,
        "images_count": len(image_urls),
        "image_urls": image_urls,
    }
