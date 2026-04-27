"""
ipoipo.cn 行业报告爬虫 - Flask 代理服务器
提供 API 接口和前端页面服务
"""

import io
import json
import os
import re
import time
import threading
import logging
from urllib.parse import unquote, quote

from flask import Flask, render_template, jsonify, request, send_file, Response
import requests

from scraper import IPOScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# 使用脚本所在目录作为根目录，避免从其他目录启动时找不到模板
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
scraper = IPOScraper()

# 缓存配置
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'reports.json')
CACHE_TTL = 3600  # 缓存有效期：1小时

# 爬取状态
scrape_status = {
    'is_scraping': False,
    'progress': '',
    'start_time': None,
}


def ensure_cache_dir():
    """确保缓存目录存在"""
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_cache():
    """从缓存文件加载数据（0条数据视为无效缓存）"""
    if os.path.exists(CACHE_FILE):
        age = time.time() - os.path.getmtime(CACHE_FILE)
        if age < CACHE_TTL:
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 缓存数据为0条时视为无效，触发重新爬取
                if data.get('total', 0) > 0:
                    logger.info(f'从缓存加载数据，共 {data.get("total", 0)} 条')
                    return data
                else:
                    logger.info('缓存数据为空，将重新爬取')
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f'缓存读取失败: {e}')
    return None


def save_cache(data):
    """保存数据到缓存文件"""
    ensure_cache_dir()
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f'数据已缓存，共 {data.get("total", 0)} 条')
    except IOError as e:
        logger.error(f'缓存写入失败: {e}')


def clear_cache():
    """清除缓存"""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        logger.info('缓存已清除')


def do_scrape(days=7, force=False):
    """执行爬取任务"""
    if not force:
        cached = load_cache()
        if cached:
            return cached

    scrape_status['is_scraping'] = True
    scrape_status['start_time'] = time.time()
    scrape_status['progress'] = '正在初始化...'

    try:
        def progress_cb(msg):
            scrape_status['progress'] = msg
            logger.info(f'[爬取进度] {msg}')

        reports = scraper.fetch_recent_reports(days=days, progress_callback=progress_cb)

        data = {
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(reports),
            'days': days,
            'reports': reports,
        }
        save_cache(data)
        return data
    except Exception as e:
        logger.error(f'爬取异常: {e}', exc_info=True)
        return {
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total': 0,
            'days': days,
            'reports': [],
            'error': str(e),
        }
    finally:
        scrape_status['is_scraping'] = False
        scrape_status['progress'] = ''


# ==================== 路由 ====================

@app.route('/')
def index():
    """返回前端页面"""
    return render_template('index.html')


@app.route('/api/reports')
def get_reports():
    """获取近N天报告数据（带缓存）"""
    days = request.args.get('days', 7, type=int)
    days = min(max(days, 1), 30)  # 限制1-30天

    # 如果正在爬取，返回状态
    if scrape_status['is_scraping']:
        return jsonify({
            'status': 'scraping',
            'progress': scrape_status['progress'],
            'elapsed': int(time.time() - scrape_status['start_time']) if scrape_status['start_time'] else 0,
        }), 202

    data = do_scrape(days=days, force=False)
    return jsonify(data)


@app.route('/api/reports/refresh')
def refresh_reports():
    """强制刷新数据（清除缓存后重新爬取）"""
    days = request.args.get('days', 7, type=int)
    days = min(max(days, 1), 30)

    if scrape_status['is_scraping']:
        return jsonify({
            'status': 'already_scraping',
            'message': '正在爬取中，请稍后再试',
            'progress': scrape_status['progress'],
        }), 409

    clear_cache()
    data = do_scrape(days=days, force=True)
    return jsonify(data)


@app.route('/api/status')
def get_status():
    """获取爬取状态"""
    return jsonify({
        'is_scraping': scrape_status['is_scraping'],
        'progress': scrape_status['progress'],
        'elapsed': int(time.time() - scrape_status['start_time']) if scrape_status['start_time'] and scrape_status['is_scraping'] else 0,
    })


@app.route('/api/proxy/download')
def proxy_download():
    """代理下载zip文件（解决跨域和防盗链）"""
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': '缺少url参数'}), 400

    url = unquote(url)

    # 安全检查：只允许下载 ipoipo.cn 域名的zip文件
    if not url.startswith('https://ipoipo.cn/') and not url.startswith('http://ipoipo.cn/'):
        return jsonify({'error': '不支持的下载域名'}), 403

    if not url.endswith('.zip'):
        return jsonify({'error': '仅支持zip文件下载'}), 400

    try:
        # 流式下载
        resp = requests.get(
            url,
            stream=True,
            headers=scraper.get_headers(),
            timeout=60
        )
        resp.raise_for_status()

        # 从title参数生成文件名，回退到URL文件名
        title = request.args.get('title', '')
        title = unquote(title)
        if title:
            # 清理文件名：移除非法字符，保留中文、字母、数字、括号等
            safe_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
            safe_title = safe_title[:200]  # 限制长度
            filename = safe_title + '.zip'
        else:
            filename = url.split('/')[-1]
            if not filename.endswith('.zip'):
                filename = 'report.zip'

        # 对中文文件名进行 RFC 5987 编码
        encoded_filename = quote(filename, safe='')

        # 构建流式响应
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        return Response(
            generate(),
            mimetype='application/zip',
            headers={
                'Content-Disposition': f"attachment; filename=\"{encoded_filename}\"; filename*=UTF-8''{encoded_filename}",
                'Content-Length': resp.headers.get('Content-Length', ''),
            }
        )
    except requests.RequestException as e:
        logger.error(f'代理下载失败: {url} - {e}')
        return jsonify({'error': f'下载失败: {str(e)}'}), 502


if __name__ == '__main__':
    ensure_cache_dir()
    logger.info('启动服务器: http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
