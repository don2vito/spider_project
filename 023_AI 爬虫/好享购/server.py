#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快乐购节目表 - 本地代理服务器
==============================
为 happigo.html 提供本地 API 代理，绕过浏览器 CORS 限制。

用法:
    python server.py              # 启动服务器（默认端口 8080）
    python server.py --port 3000  # 指定端口

启动后浏览器打开 http://localhost:8080/happigo.html 即可使用。
"""

import argparse
import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

import requests as req_lib


# 目标 API 的固定请求头
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Content-Type': 'application/json; charset=utf-8',
    'Origin': 'https://m.hao24.com',
    'Referer': 'https://m.hao24.com/live/today.html',
    'X-Requested-With': 'XMLHttpRequest',
}


class ProxyHandler(SimpleHTTPRequestHandler):
    """带 API 代理功能的静态文件服务器"""

    def do_POST(self):
        if self.path == '/api/proxy' or self.path.startswith('/api/'):
            self.handle_proxy()
        else:
            self.send_error(405, 'Method Not Allowed')

    def handle_proxy(self):
        """转发请求到目标 URL"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length)

            # 尝试解析为 JSON
            try:
                params = json.loads(raw_body.decode('utf-8'))
            except json.JSONDecodeError:
                # 如果不是 JSON，直接作为 body 转发
                params = {}

            target_url = params.get('targetUrl', '')
            method = params.get('method', 'POST').upper()
            req_body = params.get('body', b'')

            if not target_url:
                self.send_json_response({'error': '缺少 targetUrl'}, 400)
                return

            # 处理 body：确保是 bytes
            if isinstance(req_body, str):
                req_body = req_body.encode('utf-8')
            elif isinstance(req_body, dict):
                req_body = json.dumps(req_body).encode('utf-8')
            elif not isinstance(req_body, bytes):
                req_body = b''

            # 发送请求
            resp = req_lib.request(method, target_url, headers=API_HEADERS, data=req_body, timeout=15)
            resp.raise_for_status()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(resp.content)

        except req_lib.exceptions.HTTPError as e:
            err_body = e.response.content[:500] if e.response.content else str(e)
            self.send_json_response({'error': f'HTTP {e.response.status_code}', 'detail': err_body.decode('utf-8', errors='replace')}, 502)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_json_response(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        msg = str(args[0]) if args else ''
        if '/api/' in msg:
            print(f"  [PROXY] {msg}")


def main():
    parser = argparse.ArgumentParser(description='快乐购节目表 - 本地代理服务器')
    parser.add_argument('--port', '-p', type=int, default=8080, help='端口号（默认：8080）')
    args = parser.parse_args()

    server = HTTPServer(('0.0.0.0', args.port), ProxyHandler)

    print()
    print("=" * 50)
    print("  📺 快乐购节目表 - 本地代理服务器")
    print("=" * 50)
    print(f"  🌐 地址: http://localhost:{args.port}/happigo.html")
    print(f"  📡 代理: http://localhost:{args.port}/api/proxy")
    print(f"  ⏹️  停止: Ctrl+C")
    print("=" * 50)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n  服务器已停止")
        server.server_close()


if __name__ == '__main__':
    main()
