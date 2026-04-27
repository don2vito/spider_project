"""
CBNData 免费报告爬虫 - Flask 主应用
提供 API 端点和前端页面服务
"""

import io
import threading
import logging
from datetime import datetime, timedelta
from urllib.parse import quote, urlparse

import requests as http_requests
from flask import Flask, jsonify, send_file, render_template, request, Response

from scraper import get_free_reports, get_report_images
from pdf_generator import generate_pdf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── 报告列表缓存 ──────────────────────────────────────────────
_cache = {"data": None, "expires": None, "year": None}
_cache_lock = threading.Lock()


def get_reports_with_cache(year=None):
    """获取报告列表（含 5 分钟内存缓存）"""
    if year is None:
        year = datetime.now().year

    now = datetime.now()

    with _cache_lock:
        if (
            _cache["data"] is not None
            and _cache["expires"] is not None
            and _cache["year"] == year
            and now < _cache["expires"]
        ):
            logger.info(f"使用缓存数据 ({len(_cache['data'])} 份报告)")
            return _cache["data"]

    # 缓存过期或不存在，重新获取
    data = get_free_reports(year=year)

    with _cache_lock:
        _cache["data"] = data
        _cache["expires"] = now + timedelta(minutes=5)
        _cache["year"] = year

    return data


# ── 并发控制 ──────────────────────────────────────────────────
# 限制最多 3 个同时进行的 PDF 生成
_pdf_semaphore = threading.Semaphore(3)


# ── 路由 ──────────────────────────────────────────────────────

@app.route('/')
def index():
    """前端页面"""
    return render_template('index.html')


@app.route('/api/proxy-image')
def api_proxy_image():
    """代理图片请求，解决跨域和 Referer 问题"""
    img_url = request.args.get('url', '')
    if not img_url:
        return Response(status=400)

    # 安全检查：仅允许特定域名
    parsed = urlparse(img_url)
    allowed_hosts = ['cf.dtcj.com', 'cfpdf.dtcj.com', 'dtcj.com']
    if parsed.hostname not in allowed_hosts:
        return Response(status=403)

    try:
        resp = http_requests.get(
            img_url,
            timeout=(10, 30),
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.cbndata.com/",
            }
        )
        resp.raise_for_status()

        content_type = resp.headers.get('Content-Type', 'image/jpeg')
        return Response(
            resp.iter_content(chunk_size=8192),
            content_type=content_type,
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
            }
        )
    except Exception as e:
        logger.warning(f"图片代理失败: {e}")
        return Response(status=502)


@app.route('/api/reports')
def api_reports():
    """
    获取当前年度免费报告列表。

    Query 参数:
        year: 目标年份（可选，默认为当前年份）
        refresh: 是否强制刷新缓存（可选，"1" 表示刷新）
    """
    try:
        year = request.args.get('year', type=int)
        refresh = request.args.get('refresh') == '1'

        if refresh:
            with _cache_lock:
                _cache["data"] = None
                _cache["expires"] = None

        reports = get_reports_with_cache(year=year)
        target_year = year or datetime.now().year

        return jsonify({
            "success": True,
            "year": target_year,
            "count": len(reports),
            "data": reports,
        })
    except Exception as e:
        logger.error(f"获取报告列表失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/report/<int:product_id>/detail')
def api_report_detail(product_id):
    """
    获取指定报告的图片 URL 列表（实时获取新 token）。
    """
    try:
        detail = get_report_images(product_id)
        return jsonify({
            "success": True,
            "data": detail,
        })
    except Exception as e:
        logger.error(f"获取报告 {product_id} 详情失败: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/report/<int:product_id>/download')
def api_report_download(product_id):
    """
    生成 PDF 并返回下载。
    每次调用都重新抓取详情页获取新的图片 token。
    """
    # 并发控制
    acquired = _pdf_semaphore.acquire(blocking=False)
    if not acquired:
        return jsonify({
            "success": False,
            "error": "服务器繁忙，请稍后重试（当前有多个 PDF 生成任务）"
        }), 429

    try:
        # 1. 实时获取图片 URL（新 token）
        logger.info(f"开始处理 PDF 下载请求: 报告 {product_id}")
        detail = get_report_images(product_id)
        image_urls = detail["image_urls"]
        title = detail["title"]

        if not image_urls:
            return jsonify({"success": False, "error": "未找到报告图片"}), 404

        # 2. 生成 PDF
        pdf_bytes, filename = generate_pdf(image_urls, title)

        # 3. 返回文件流
        response = send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )

        # 处理中文文件名编码（RFC 5987）
        response.headers['Content-Disposition'] = (
            f"attachment; filename*=UTF-8''{quote(filename)}"
        )

        logger.info(f"PDF 下载完成: {filename}")
        return response

    except Exception as e:
        logger.error(f"PDF 生成失败 (报告 {product_id}): {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        _pdf_semaphore.release()


# ── 启动 ──────────────────────────────────────────────────────

if __name__ == '__main__':
    logger.info("启动 CBNData 报告爬虫服务器...")
    logger.info("访问 http://localhost:5000 查看报告列表")
    app.run(host='0.0.0.0', port=5000, debug=True)
