# -*- coding: utf-8 -*-
"""
巨潮资讯网公告爬虫 - Flask 代理服务器
提供 API 接口供前端 HTML 应用调用，代理爬取 cninfo.com.cn 公告数据
"""

import io
import os
import re
import time
import random
import zipfile
import traceback
from datetime import datetime

import requests
from flask import Flask, request, Response, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ============ 常量配置 ============

CNINFO_API_URL = 'https://www.cninfo.com.cn/new/hisAnnouncement/query'
CNINFO_HOME_URL = 'https://www.cninfo.com.cn/'
PDF_BASE_URL = 'https://static.cninfo.com.cn/'

HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.cninfo.com.cn",
    "Origin": "https://www.cninfo.com.cn",
    "Referer": "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

# 全局 requests Session
session = requests.Session()
session.headers.update({
    "User-Agent": HEADERS["User-Agent"],
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
})

# ============ 初始化会话 ============

def init_session():
    """首次访问 cninfo 首页获取 Cookie"""
    try:
        session.get(CNINFO_HOME_URL, timeout=10)
        print("[✓] 会话初始化成功，Cookie 已获取")
    except Exception as e:
        print(f"[✗] 会话初始化失败: {e}")

init_session()

# ============ SSE 进度通知辅助 ============

def sse_event(data: dict):
    """生成 Server-Sent Events 格式数据"""
    import json
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

# ============ API 路由 ============

@app.route('/')
def index():
    """返回前端 HTML 页面"""
    return send_from_directory('.', 'index.html')


@app.route('/api/stock-search')
def api_stock_search():
    """代理搜索股票代码/简称，返回匹配的股票列表（含 orgId）"""
    keyword = request.args.get('keyword', '').strip()
    if not keyword or len(keyword) < 1:
        return jsonify([])

    try:
        url = 'https://www.cninfo.com.cn/new/information/topSearch/query'
        payload = {
            'keyWord': keyword,
            'maxSecNum': 10,
            'maxListNum': 5,
        }
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.cninfo.com.cn",
            "Referer": "https://www.cninfo.com.cn/",
            "X-Requested-With": "XMLHttpRequest",
        }
        resp = session.get(url, params=payload, headers=headers, timeout=10)
        data = resp.json()

        results = []
        # 解析返回数据，格式通常为 { codeList: [...], titleList: [...] }
        for item in data.get('codeList', []):
            results.append({
                'orgId': item.get('orgId', ''),
                'code': item.get('code', ''),
                'shortName': item.get('shortName', ''),
                'category': item.get('category', ''),
            })
        return jsonify(results)
    except Exception as e:
        print(f"[!] Stock search error: {e}")
        return jsonify([])


@app.route('/api/search', methods=['POST'])
def api_search():
    """
    代理搜索公告 - 使用 SSE 流式返回进度和结果
    前端通过 EventSource 或 fetch + ReadableStream 接收
    """
    # 必须在生成器外部获取请求参数（避免请求上下文丢失）
    params = request.json or {}

    def generate():
        import json

        # 提取参数
        stock = params.get('stock', '').strip()
        searchkey = params.get('searchkey', '').strip()
        plate = params.get('plate', '').strip()
        trade = params.get('trade', '').strip()
        category = params.get('category', '').strip()
        date_start = params.get('date_start', '').strip()
        date_end = params.get('date_end', '').strip()

        # 验证日期
        if not date_start or not date_end:
            yield sse_event({"type": "error", "message": "请选择日期范围"})
            return

        # 构造日期参数
        se_date = f"{date_start}~{date_end}"

        # 构造 payload
        payload = {
            'pageNum': '1',
            'pageSize': '100',
            'column': 'szse',
            'tabName': 'fulltext',
            'plate': plate,
            'stock': stock,
            'searchkey': searchkey,
            'secid': '',
            'category': category,
            'trade': trade,
            'seDate': se_date,
            'sortName': '',
            'sortType': '',
            'isHLtitle': 'true',
        }

        all_data = []
        page = 1
        total_pages = 0
        total_announcements = 0

        yield sse_event({"type": "status", "message": "正在连接巨潮资讯网..."})

        while True:
            payload['pageNum'] = str(page)

            # 指数退避重试
            for retry in range(5):
                try:
                    resp = session.post(CNINFO_API_URL, headers=HEADERS, data=payload, timeout=30)

                    # 检查响应状态
                    if resp.status_code != 200:
                        raise Exception(f"HTTP {resp.status_code}")

                    # 尝试解析 JSON
                    try:
                        result = resp.json()
                    except Exception:
                        # 打印实际响应内容用于调试
                        print(f"[DEBUG] Non-JSON response (status={resp.status_code}, len={len(resp.text)}): {resp.text[:200]}")
                        raise Exception(f"响应解析失败: {resp.text[:100]}")

                    # 检查是否被频率限制
                    if isinstance(result, str) and '频繁' in result:
                        raise Exception("访问过于频繁")

                    # 检查是否有 announcements 字段
                    if not isinstance(result, dict):
                        raise Exception(f"异常响应: {str(result)[:100]}")

                    break
                except Exception as e:
                    if retry < 4:
                        wait_time = (2 ** (retry + 1)) + random.uniform(1, 3)
                        yield sse_event({
                            "type": "status",
                            "message": f"请求受限，等待 {wait_time:.1f} 秒后重试 ({retry + 1}/5)..."
                        })
                        time.sleep(wait_time)
                    else:
                        yield sse_event({"type": "error", "message": f"数据抓取失败（已重试5次）: {str(e)}"})
                        return

            # 解析响应 - 确保 announcements 是列表
            announcements = result.get('announcements') or []
            total_announcements = result.get('totalAnnouncement', 0) or 0
            total_pages = result.get('totalpages', 0) or 0
            has_more = result.get('hasMore', False)

            if page == 1:
                yield sse_event({
                    "type": "status",
                    "message": f"共找到 {total_announcements} 条公告，正在抓取..."
                })

            # 处理数据
            for item in announcements:
                ann_time = item.get('announcementTime', 0)
                if ann_time:
                    ann_time_str = datetime.fromtimestamp(ann_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    ann_time_str = ''

                adjunct_url = item.get('adjunctUrl', '')
                pdf_url = f"{PDF_BASE_URL}{adjunct_url}" if adjunct_url else ''

                all_data.append({
                    'secCode': item.get('secCode', ''),
                    'secName': item.get('secName', ''),
                    'title': item.get('announcementTitle', ''),
                    'time': ann_time_str,
                    'timestamp': ann_time,
                    'pdfUrl': pdf_url,
                    'adjunctSize': item.get('adjunctSize', 0),
                    'adjunctType': item.get('adjunctType', ''),
                    'announcementId': item.get('announcementId', ''),
                })

            yield sse_event({
                "type": "progress",
                "page": page,
                "totalPages": total_pages,
                "totalFetched": len(all_data),
                "totalAnnouncements": total_announcements,
                "message": f"正在抓取第 {page}/{total_pages} 页 ({len(all_data)}/{total_announcements})..."
            })

            if not has_more or not announcements:
                break

            # 安全检查：如果已获取数据超过总数，停止翻页
            if total_announcements > 0 and len(all_data) >= total_announcements:
                break

            page += 1
            # 随机延迟 2-4 秒
            delay = random.uniform(2, 4)
            time.sleep(delay)

        # 返回最终结果
        yield sse_event({
            "type": "complete",
            "total": len(all_data),
            "data": all_data,
            "message": f"抓取完成，共 {len(all_data)} 条公告"
        })

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.route('/api/download')
def api_download():
    """代理下载单个 PDF 文件"""
    pdf_url = request.args.get('url', '')
    if not pdf_url:
        return jsonify({"error": "缺少 url 参数"}), 400

    try:
        resp = session.get(pdf_url, stream=True, timeout=60)
        resp.raise_for_status()

        # 从 URL 提取文件名
        filename = pdf_url.split('/')[-1]
        # 清理文件名中的非法字符
        filename = re.sub(r'[\\/:*?"<>|]', '_', filename)

        return Response(
            resp.iter_content(chunk_size=8192),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f"attachment; filename*=UTF-8''{filename}",
                'Content-Length': resp.headers.get('Content-Length', ''),
            }
        )
    except Exception as e:
        return jsonify({"error": f"下载失败: {str(e)}"}), 500


@app.route('/api/download-all', methods=['POST'])
def api_download_all():
    """打包下载全部 PDF 为 ZIP"""
    files = request.json.get('files', [])
    if not files:
        return jsonify({"error": "文件列表为空"}), 400

    def generate():
        zip_buffer = io.BytesIO()
        total = len(files)

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, f in enumerate(files):
                url = f.get('url', '')
                filename = f.get('filename', f'file_{i}.pdf')
                # 清理文件名
                filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
                # 确保扩展名
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'

                try:
                    resp = session.get(url, timeout=60)
                    resp.raise_for_status()
                    zf.writestr(filename, resp.content)
                except Exception as e:
                    print(f"[!] 下载失败 {filename}: {e}")
                    zf.writestr(f"FAILED_{filename}.txt", f"下载失败: {str(e)}")

                # 每下载一个文件后 yield 进度
                progress = {
                    "type": "progress",
                    "current": i + 1,
                    "total": total,
                    "filename": filename,
                }
                import json
                yield f"data: {json.dumps(progress, ensure_ascii=False)}\n\n"

                # 小延迟避免过快
                time.sleep(0.3)

        zip_buffer.seek(0)

        # 发送完成信号
        import json
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        # 发送 ZIP 文件
        yield zip_buffer.getvalue()

    # 使用 multipart 混合响应
    return Response(
        generate(),
        mimetype='application/octet-stream',
        headers={
            'Content-Disposition': 'attachment; filename*=UTF-8\'\'announcements.zip',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


@app.route('/api/download-all-zip', methods=['POST'])
def api_download_all_zip():
    """打包下载全部 PDF 为 ZIP（同步版本，更可靠）"""
    files = request.json.get('files', [])
    if not files:
        return jsonify({"error": "文件列表为空"}), 400

    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, f in enumerate(files):
                url = f.get('url', '')
                filename = f.get('filename', f'file_{i}.pdf')
                filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'

                try:
                    resp = session.get(url, timeout=60)
                    resp.raise_for_status()
                    zf.writestr(filename, resp.content)
                except Exception as e:
                    print(f"[!] 下载失败 {filename}: {e}")
                    zf.writestr(f"FAILED_{filename}.txt", f"下载失败: {str(e)}")

                time.sleep(0.3)

        zip_buffer.seek(0)
        return Response(
            zip_buffer.getvalue(),
            mimetype='application/zip',
            headers={
                'Content-Disposition': "attachment; filename*=UTF-8''announcements.zip",
            }
        )
    except Exception as e:
        return jsonify({"error": f"打包下载失败: {str(e)}"}), 500


# ============ 启动 ============

if __name__ == '__main__':
    print("=" * 60)
    print("  巨潮资讯网公告爬虫 - 代理服务器")
    print("=" * 60)
    print(f"  服务地址: http://localhost:5000")
    print(f"  前端页面: http://localhost:5000/index.html")
    print("=" * 60)
    print("  按 Ctrl+C 停止服务器")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
