#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聚鲨环球精选 · 节目表 本地服务器
=================================
提供HTML页面 + API代理，解决浏览器CORS跨域限制。

用法:
    python shark_server.py              # 启动服务器（默认端口 5000）
    python shark_server.py --port 8080  # 指定端口

启动后浏览器打开 http://localhost:5000 即可使用。
"""

import hashlib
import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs

# ============================================================
# 常量配置
# ============================================================

API_BASE_URL = "https://api.sharkshopping.com/ec/api"
SECRET_KEY = "e662633040d6a433d48580a38fcedc49c9ba5d015dccf701096abade0c623163"
DEFAULT_PARAMS = {
    "appid": "webapp",
    "token": "",
    "version": "4.4.1",
    "source": "wap",
    "city_num": "310100",
    "oriSource": "wap",
}
CST = timezone(timedelta(hours=8))

# HTML文件目录
HTML_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# 签名模块
# ============================================================

def md5_sign(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def generate_sign(params: dict) -> str:
    sorted_keys = sorted(params.keys())
    concat_str = ""
    for key in sorted_keys:
        value = params[key]
        if value is None or isinstance(value, list):
            continue
        if isinstance(value, dict):
            value = json.dumps(value, separators=(",", ":"))
        concat_str += str(key) + str(value)
    first_md5 = md5_sign(concat_str).upper()
    return md5_sign(first_md5 + SECRET_KEY).upper()


def build_request_params(method: str, **extra_params) -> dict:
    params = {**DEFAULT_PARAMS, **extra_params}
    params["timestamp"] = str(int(time.time() * 1000))
    params["method"] = method
    params["sign"] = generate_sign(params)
    return params


# ============================================================
# API请求模块
# ============================================================

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.parse
    HAS_REQUESTS = False


def http_get(url: str, params: dict) -> dict:
    """发送HTTP GET请求"""
    query = urlencode({k: v for k, v in params.items() if k != "method"})
    full_url = f"{url}?method={params.get('method', '')}&{query}"

    if HAS_REQUESTS:
        resp = _requests.get(full_url, timeout=15,
                             headers={
                                 "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/91.0.4472.120 Mobile Safari/537.36",
                                 "Accept": "application/json",
                                 "Referer": "https://wp.sharkshopping.com/programs_list",
                             })
        resp.raise_for_status()
        return resp.json()
    else:
        req = urllib.request.Request(full_url, headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/91.0.4472.120 Mobile Safari/537.36",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))


def api_request(method: str, **extra_params) -> dict:
    """调用聚鲨API"""
    params = build_request_params(method, **extra_params)
    data = http_get(API_BASE_URL, params)
    if data.get("rsp") == "succ":
        return data.get("data", {}).get("returndata", {})
    return {}


def get_available_dates() -> list:
    data = api_request("tv.program.date")
    return data if isinstance(data, list) else []


def get_program_data(date: str) -> dict:
    return api_request("tv.program.data", date=date, brand_id="", cat_id="")


# ============================================================
# HTTP服务器
# ============================================================

class SharkHandler(SimpleHTTPRequestHandler):
    """自定义HTTP处理器：提供静态文件 + API代理"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HTML_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        # API代理路由
        if parsed.path == "/api/dates":
            self._handle_api_dates()
        elif parsed.path == "/api/programs":
            query = parse_qs(parsed.query)
            date = query.get("date", [datetime.now(CST).strftime("%Y-%m-%d")])[0]
            self._handle_api_programs(date)
        elif parsed.path == "/api/all":
            self._handle_api_all()
        else:
            # 静态文件服务
            super().do_GET()

    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _handle_api_dates(self):
        try:
            dates = get_available_dates()
            self._send_json({"success": True, "data": dates})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    def _handle_api_programs(self, date: str):
        try:
            raw = get_program_data(date)
            channel = raw.get("channel", {})
            program_data = raw.get("program_data", [])
            programs = []
            for item in program_data:
                if item.get("goods"):
                    programs.append(self._parse_item(item))
            self._send_json({
                "success": True,
                "channel": channel,
                "programs": programs,
                "date": date
            })
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    def _handle_api_all(self):
        try:
            dates = get_available_dates()
            if not dates:
                self._send_json({"success": False, "error": "无法获取日期列表"}, 500)
                return

            all_programs = []
            for d in dates:
                raw = get_program_data(d["real_date"])
                for item in raw.get("program_data", []):
                    if item.get("goods"):
                        all_programs.append(self._parse_item(item))
                time.sleep(0.3)

            # 按日期升序、时间升序排列
            all_programs.sort(key=lambda x: (x["日期"], x["开始时间"]))

            self._send_json({
                "success": True,
                "dates": dates,
                "programs": all_programs,
                "total": len(all_programs)
            })
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    @staticmethod
    def _parse_item(item: dict) -> dict:
        goods = item.get("goods") or {}
        discount = ""
        jz = goods.get("jz_label")
        dl = goods.get("discount_label")
        if jz:
            discount = jz.get("labelName", "")
        elif dl:
            discount = dl.get("labelName", "")
        if not discount:
            discount = goods.get("description", "")

        def ts_to_time(ts):
            if not ts or ts <= 0:
                return "--:--"
            dt = datetime.fromtimestamp(ts, tz=CST)
            return dt.strftime("%H:%M")

        return {
            "日期": item.get("real_date", ""),
            "显示日期": item.get("show_date", ""),
            "开始时间": ts_to_time(item.get("start_time", 0)),
            "结束时间": ts_to_time(item.get("end_time", 0)),
            "分类": item.get("cat_name", ""),
            "品牌": item.get("brand_name", ""),
            "商品名称": goods.get("name", ""),
            "SKU": goods.get("sku", ""),
            "手机价": goods.get("price", ""),
            "市场价": goods.get("marketprice", ""),
            "优惠信息": discount,
            "商品链接": goods.get("wapUrl", ""),
            "商品图片": goods.get("image", ""),
            "一级分类": goods.get("product_first", ""),
            "二级分类": goods.get("product_second", ""),
            "三级分类": goods.get("product_third", ""),
        }

    def log_message(self, format, *args):
        # 简化日志输出
        if "/api/" in str(args[0]):
            print(f"  [API] {args[0]}")
        # 静态文件请求不打印


def main():
    parser = argparse.ArgumentParser(description="聚鲨环球精选 · 节目表本地服务器")
    parser.add_argument("--port", "-p", type=int, default=5000, help="端口号 (默认: 5000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="主机地址 (默认: 0.0.0.0)")
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), SharkHandler)

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║     📺 聚鲨环球精选 · 节目表 本地服务器      ║")
    print("  ╠══════════════════════════════════════════════╣")
    print(f"  ║  地址: http://localhost:{args.port}              ║")
    print("  ║  按 Ctrl+C 停止服务器                       ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  服务器已停止。")
        server.server_close()


if __name__ == "__main__":
    main()
