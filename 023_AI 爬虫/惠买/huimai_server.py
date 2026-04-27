#!/usr/bin/env python3
"""
惠买网电视购物节目表 - 本地代理服务器
解决浏览器CORS限制，为HTML前端提供数据代理接口
"""
import http.server
import json
import urllib.request
import urllib.parse
import sys
from datetime import datetime, timedelta

PORT = 8765
API_URL = "https://www.huimai.com.cn/getTvList"
PAGE_URL = "https://www.huimai.com.cn/tvList"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.huimai.com.cn/tvList",
    "Origin": "https://www.huimai.com.cn",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

CHANNELS = {"UGO1": "优购物", "BTV1": "爱家购物"}
DAYS = 7


def get_date_range(days=7):
    """获取最近N天的日期列表"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    for i in range(days):
        d = today - timedelta(days=i)
        ts = int(d.timestamp())
        date_str = d.strftime("%Y-%m-%d")
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday = weekdays[d.weekday()]
        result.append({"date": date_str, "timestamp": ts, "weekday": weekday})
    return result


def fetch_tvlist(channel, date_timestamp):
    """调用API获取单日单频道节目表"""
    data = urllib.parse.urlencode({"channel": channel, "date": str(date_timestamp)}).encode()
    req = urllib.request.Request(API_URL, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"code": -1, "msg": str(e), "data": None}


def parse_tvlist(api_data, channel, channel_name, date_str, weekday):
    """解析API返回数据"""
    programs = []
    if not api_data or not api_data.get("data"):
        return programs
    for group in api_data["data"].get("tvItemList", []):
        if not group or len(group) == 0:
            continue
        item = group[0]
        programs.append({
            "date": date_str,
            "weekday": weekday,
            "channel": channel_name,
            "channelKey": channel,
            "begin": item.get("begin", ""),
            "end": item.get("end", ""),
            "goodsId": item.get("goodsId", ""),
            "goodsName": item.get("goodsName", ""),
            "price": item.get("price", ""),
            "shopPrice": item.get("shopPrice", ""),
            "actLabelDesc": item.get("actLabelDesc", ""),
            "isLiving": item.get("isLiving") == "1",
            "goodsUrl": f"https://www.huimai.com.cn/goods-{item.get('goodsId', '')}.html",
            "imageUrl": item.get("mainPicUrl", ""),
        })
    return programs


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP请求处理器：代理API + 静态文件"""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # API: 获取所有节目数据
        if parsed.path == "/api/tvlist":
            self.send_api_response()
            return

        # API: 健康检查
        if parsed.path == "/api/health":
            self.send_json(200, {"status": "ok"})
            return

        # 静态文件
        super().do_GET()

    def send_api_response(self):
        """获取所有频道所有日期的节目数据"""
        date_range = get_date_range(DAYS)
        all_programs = []

        for ch_key, ch_name in CHANNELS.items():
            for day_info in date_range:
                api_data = fetch_tvlist(ch_key, day_info["timestamp"])
                programs = parse_tvlist(
                    api_data, ch_key, ch_name,
                    day_info["date"], day_info["weekday"]
                )
                all_programs.extend(programs)

        # 排序：频道(优购物在前) → 日期升序 → 时间升序
        channel_order = {"UGO1": 0, "BTV1": 1}
        all_programs.sort(key=lambda p: (
            channel_order.get(p["channelKey"], 9),
            p["date"],
            p["begin"]
        ))

        self.send_json(200, {
            "success": True,
            "total": len(all_programs),
            "channels": list(CHANNELS.values()),
            "days": DAYS,
            "programs": all_programs,
        })

    def send_json(self, code, data):
        """发送JSON响应"""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, format, *args):
        """简化日志输出"""
        if "/api/" in str(args[0]):
            print(f"  [API] {args[0]}")
        # 静态文件请求不打印


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")

    print(f"╔══════════════════════════════════════════════╗")
    print(f"║  惠买网电视购物节目表 - 本地代理服务器       ║")
    print(f"╠══════════════════════════════════════════════╣")
    print(f"║  服务地址: http://localhost:{PORT}             ║")
    print(f"║  API接口:  http://localhost:{PORT}/api/tvlist  ║")
    print(f"║  按 Ctrl+C 停止服务器                        ║")
    print(f"╚══════════════════════════════════════════════╝")
    print()

    server = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.server_close()
