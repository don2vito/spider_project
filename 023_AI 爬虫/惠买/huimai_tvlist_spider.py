#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
惠买网(www.huimai.com.cn) 电视购物节目表爬虫
=============================================
功能：获取"优购物"和"爱家购物"两个频道每天的节目表信息
接口：POST https://www.huimai.com.cn/getTvList
参数：channel(频道key) + date(Unix时间戳)
"""

import requests
import json
import csv
import time
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ============================================================
# 常量定义
# ============================================================

BASE_URL = "https://www.huimai.com.cn"
API_PATH = "/getTvList"
API_URL = BASE_URL + API_PATH

# 频道配置：key => 频道名称
CHANNELS = {
    "UGO1": "优购物",
    "BTV1": "爱家购物",
}

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.huimai.com.cn/tvList",
    "Origin": "https://www.huimai.com.cn",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

# 时区：东八区
TZ_SHANGHAI = ZoneInfo("Asia/Shanghai")

# 请求超时（秒）
REQUEST_TIMEOUT = 15

# 重试次数
MAX_RETRIES = 3

# 请求间隔（秒），避免过于频繁
REQUEST_DELAY = 0.5


# ============================================================
# 工具函数
# ============================================================

def date_to_timestamp(date_str: str) -> int:
    """
    日期字符串转Unix时间戳（秒），基于东八区当天00:00:00
    支持格式：YYYY-MM-DD
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=TZ_SHANGHAI)
    return int(dt.timestamp())


def timestamp_to_date(ts: int) -> str:
    """Unix时间戳转日期字符串 YYYY-MM-DD"""
    dt = datetime.fromtimestamp(ts, tz=TZ_SHANGHAI)
    return dt.strftime("%Y-%m-%d")


def get_date_range(days: int = 7) -> list:
    """
    获取最近N天的日期列表（从今天往回推）
    返回：[(date_str, timestamp), ...]
    """
    today = datetime.now(TZ_SHANGHAI).replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    for i in range(days):
        d = today - timedelta(days=i)
        ts = int(d.timestamp())
        date_str = d.strftime("%Y-%m-%d")
        result.append((date_str, ts))
    return result


def get_weekday_name(date_str: str) -> str:
    """获取日期对应的星期名称"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return weekdays[dt.weekday()]


# ============================================================
# 核心爬虫函数
# ============================================================

def create_session() -> requests.Session:
    """创建HTTP会话"""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def fetch_tvlist(session: requests.Session, channel: str, date_timestamp: int) -> dict:
    """
    调用API获取单日单频道的节目表

    参数：
        session: requests会话
        channel: 频道key (UGO1/BTV1)
        date_timestamp: Unix时间戳

    返回：
        API返回的JSON数据(dict)
    """
    payload = {
        "channel": channel,
        "date": str(date_timestamp),
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.post(API_URL, data=payload, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            result = resp.json()

            if result.get("code") == 0 and result.get("data"):
                return result
            else:
                print(f"  [警告] API返回异常: code={result.get('code')}, msg={result.get('msg')}")

        except requests.exceptions.Timeout:
            print(f"  [重试 {attempt}/{MAX_RETRIES}] 请求超时...")
        except requests.exceptions.ConnectionError:
            print(f"  [重试 {attempt}/{MAX_RETRIES}] 连接失败...")
        except json.JSONDecodeError:
            print(f"  [重试 {attempt}/{MAX_RETRIES}] JSON解析失败...")
        except Exception as e:
            print(f"  [重试 {attempt}/{MAX_RETRIES}] 未知错误: {e}")

        if attempt < MAX_RETRIES:
            time.sleep(2 * attempt)  # 递增等待

    return {"code": -1, "msg": "请求失败", "data": None}


def parse_tvlist(api_data: dict, channel: str, channel_name: str, date_str: str) -> list:
    """
    解析API返回的数据，提取节目表信息

    返回：
        节目列表，每项为一个字典
    """
    programs = []

    if not api_data or not api_data.get("data"):
        return programs

    data = api_data["data"]
    tv_item_list = data.get("tvItemList", [])

    for item_group in tv_item_list:
        if not item_group or len(item_group) == 0:
            continue

        item = item_group[0]

        program = {
            "日期": date_str,
            "星期": get_weekday_name(date_str),
            "频道": channel_name,
            "频道Key": channel,
            "开始时间": item.get("begin", ""),
            "结束时间": item.get("end", ""),
            "商品ID": item.get("goodsId", ""),
            "商品名称": item.get("goodsName", ""),
            "售价": item.get("price", ""),
            "原价": item.get("shopPrice", ""),
            "活动标签": item.get("actLabelDesc", ""),
            "商品链接": f"https://www.huimai.com.cn/goods-{item.get('goodsId', '')}.html",
            "是否直播": "是" if item.get("isLiving") == "1" else "否",
            "商品图片": item.get("mainPicUrl", ""),
        }
        programs.append(program)

    return programs


def crawl_channel(session: requests.Session, channel: str, channel_name: str,
                  days: int = 7) -> list:
    """
    爬取指定频道最近N天的节目表

    参数：
        session: requests会话
        channel: 频道key
        channel_name: 频道名称
        days: 天数

    返回：
        所有节目列表
    """
    all_programs = []
    date_range = get_date_range(days)

    print(f"\n{'='*60}")
    print(f"  正在爬取【{channel_name}】最近 {days} 天的节目表...")
    print(f"{'='*60}")

    for date_str, timestamp in date_range:
        print(f"\n  📅 {date_str} ({get_weekday_name(date_str)}) ...", end=" ")

        api_data = fetch_tvlist(session, channel, timestamp)
        programs = parse_tvlist(api_data, channel, channel_name, date_str)

        if programs:
            print(f"✅ 获取到 {len(programs)} 个节目")
        else:
            print("⚠️  无数据")

        all_programs.extend(programs)
        time.sleep(REQUEST_DELAY)

    return all_programs


# ============================================================
# 输出函数
# ============================================================

def print_table(programs: list):
    """格式化打印节目表"""
    if not programs:
        print("\n暂无节目数据")
        return

    # 按日期和频道分组
    current_date = ""
    current_channel = ""

    for p in programs:
        if p["日期"] != current_date or p["频道"] != current_channel:
            current_date = p["日期"]
            current_channel = p["频道"]
            weekday = get_weekday_name(current_date)
            print(f"\n{'─'*70}")
            print(f"  📺 {current_channel} | {current_date} ({weekday})")
            print(f"{'─'*70}")
            print(f"  {'时间':<14} {'商品名称':<30} {'售价':>6}  {'标签'}")
            print(f"  {'─'*14} {'─'*30} {'─'*6}  {'─'*10}")

        time_range = f"{p['开始时间']}~{p['结束时间']}"
        name = p['商品名称'][:28] + ".." if len(p['商品名称']) > 28 else p['商品名称']
        price = f"¥{p['售价']}"
        tag = p['活动标签']
        live = " 🔴直播" if p['是否直播'] == "是" else ""

        print(f"  {time_range:<14} {name:<30} {price:>6}  {tag}{live}")


def save_to_csv(programs: list, filename: str = "huimai_tvlist.csv"):
    """保存节目表为CSV文件"""
    if not programs:
        print("\n暂无数据可保存")
        return

    # 字段顺序
    fieldnames = [
        "日期", "星期", "频道", "开始时间", "结束时间",
        "商品ID", "商品名称", "售价", "原价", "活动标签",
        "是否直播", "商品链接", "商品图片"
    ]

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(programs)

    print(f"\n✅ 数据已保存到: {filepath}")
    print(f"   共 {len(programs)} 条记录")


def save_to_json(programs: list, filename: str = "huimai_tvlist.json"):
    """保存节目表为JSON文件"""
    if not programs:
        print("\n暂无数据可保存")
        return

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(programs, f, ensure_ascii=False, indent=2)

    print(f"✅ 数据已保存到: {filepath}")
    print(f"   共 {len(programs)} 条记录")


# ============================================================
# 主函数
# ============================================================

def main(days: int = 7, save_csv: bool = True, save_json: bool = True):
    """
    主入口函数

    参数：
        days: 获取最近几天的节目表（默认7天）
        save_csv: 是否保存CSV文件
        save_json: 是否保存JSON文件
    """
    print("=" * 60)
    print("  惠买网电视购物节目表爬虫")
    print("  目标网站: www.huimai.com.cn/tvList")
    print(f"  爬取范围: 最近 {days} 天")
    print(f"  频道: 优购物(UGO1) + 爱家购物(BTV1)")
    print("=" * 60)

    session = create_session()
    all_programs = []

    # 爬取所有频道
    for channel_key, channel_name in CHANNELS.items():
        programs = crawl_channel(session, channel_key, channel_name, days)
        all_programs.extend(programs)

    # 打印结果
    print(f"\n\n{'#'*60}")
    print(f"  📊 爬取完成！共获取 {len(all_programs)} 条节目数据")
    print(f"{'#'*60}")

    print_table(all_programs)

    # 保存文件
    if save_csv:
        save_to_csv(all_programs)
    if save_json:
        save_to_json(all_programs)

    return all_programs


if __name__ == "__main__":
    # 默认获取最近7天数据
    # 可修改参数：days=7, save_csv=True, save_json=True
    main(days=7, save_csv=True, save_json=True)
