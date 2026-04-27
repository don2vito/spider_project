#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快乐购 TV5 节目表 — 本地服务器
==============================
用法: python server.py
然后打开浏览器访问 http://localhost:8080
"""

import http.server
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PORT = 8080
HTML_FILE = Path(__file__).parent / "happigo_schedule.html"
API_URL = "https://www.happigo.com/tv5/index.php?act=tv_live&op=ajaxTvzhiboGoods"


class HappigoHandler(http.server.SimpleHTTPRequestHandler):
    """同时提供 HTML 页面和 API 代理的 HTTP 处理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HTML_FILE.parent), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # API 代理端点
        if parsed.path == "/api/proxy":
            self._handle_proxy(parsed)
            return

        # 根路径 "/" 重定向到 HTML 页面
        if parsed.path == "/":
            self.send_response(302)
            self.send_header("Location", "/happigo_schedule.html")
            self.end_headers()
            return

        # 默认：提供静态文件
        super().do_GET()

    def _handle_proxy(self, parsed):
        """代理请求快乐购 API，添加必需的 Referer 头"""
        params = urllib.parse.parse_qs(parsed.query)
        ymd = params.get("ymd", [""])[0]

        if not ymd:
            self._send_json({"state": 0, "msg": "缺少 ymd 参数"}, 400)
            return

        # 构建目标 URL
        target_url = f"{API_URL}&token=ok&type=info&ymd={ymd}"

        # 创建请求，添加 Referer 头
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.happigo.com/tv5/",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self._send_json(data, 200)
        except urllib.error.HTTPError as e:
            self._send_json({"state": 0, "msg": f"上游服务器错误: {e.code}"}, 502)
        except Exception as e:
            self._send_json({"state": 0, "msg": f"请求失败: {str(e)}"}, 500)

    def _send_json(self, data, status_code):
        """发送 JSON 响应，带 CORS 头"""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # CORS 头，允许本地页面访问
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, format, *args):
        """自定义日志格式"""
        msg = format % args
        if "/api/proxy" in msg:
            print(f"  [API] {msg}")
        else:
            print(f"  [WEB] {msg}")


def main():
    if not HTML_FILE.exists():
        print(f"[错误] 找不到 {HTML_FILE}")
        print(f"请确保 happigo_schedule.html 与 server.py 在同一目录下")
        sys.exit(1)

    with http.server.HTTPServer(("0.0.0.0", PORT), HappigoHandler) as httpd:
        print()
        print(f"  ╔══════════════════════════════════════════╗")
        print(f"  ║   快乐购 TV5 节目表 — 本地服务器已启动    ║")
        print(f"  ╠══════════════════════════════════════════╣")
        print(f"  ║                                          ║")
        print(f"  ║   请在浏览器中打开:                       ║")
        print(f"  ║   http://localhost:{PORT}                  ║")
        print(f"  ║                                          ║")
        print(f"  ║   按 Ctrl+C 停止服务器                    ║")
        print(f"  ╚══════════════════════════════════════════╝")
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  服务器已停止。")


if __name__ == "__main__":
    main()
