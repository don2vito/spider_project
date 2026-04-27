#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快乐购（好享购物）每日节目表爬虫
================================
从 hao24.com 获取每日直播节目表信息，支持全量爬取多日数据。

API 接口: https://m.hao24.com/live/list.do
方法: POST (application/json)

用法:
    python happigo_scraper.py                        # 获取最近7天节目表（默认）
    python happigo_scraper.py --days 30              # 获取最近30天节目表
    python happigo_scraper.py --date 20260423        # 获取指定单日节目表
    python happigo_scraper.py --start 20260401 --end 20260424  # 指定日期范围
    python happigo_scraper.py --area 03              # 获取省外节目表
    python happigo_scraper.py --csv output.csv       # 导出为 CSV 文件
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timedelta

import requests

# ==================== 配置 ====================

API_URL = "https://m.hao24.com/live/list.do"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 12; SM-G991B) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/json; charset=utf-8",
    "Origin": "https://m.hao24.com",
    "Referer": "https://m.hao24.com/live/today.html",
    "X-Requested-With": "XMLHttpRequest",
}

# 区域代码映射
AREA_MAP = {
    "02": "省内（江苏）",
    "03": "省外",
}

# 直播状态映射
STATUS_MAP = {
    "0": "🔴 正在直播",
    "1": "🟡 即将开播",
    "2": "⚫ 已结束",
    "-1": "⚪ 其他",
    "-2": "⚫ 已结束",
}

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒
REQUEST_INTERVAL = 0.5  # 请求间隔（秒），避免频繁请求


# ==================== 核心函数 ====================


def fetch_program_list(date_str: str, area_cd: str = "02") -> dict:
    """
    从 API 获取单日节目表原始 JSON 数据。

    Args:
        date_str: 日期字符串，格式 YYYYMMDD
        area_cd: 区域代码，"02"=省内，"03"=省外

    Returns:
        API 返回的 JSON 字典
    """
    payload = {
        "date": date_str,
        "areaCd": area_cd,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("state"):
                raise ValueError(f"API 返回失败: {data}")

            return data

        except requests.RequestException as e:
            print(f"  ⚠️  第 {attempt}/{MAX_RETRIES} 次请求失败: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise


def parse_programs(data: dict, date_str: str) -> list[dict]:
    """
    解析 API 返回数据，提取节目列表，并附加日期字段。

    Args:
        data: API 返回的 JSON 字典
        date_str: 日期字符串（YYYYMMDD）

    Returns:
        节目信息字典列表
    """
    programs = []
    livelist = data.get("livelist", [])

    for item in livelist:
        goods = item.get("liveGoods", {})
        price_raw = goods.get("salePrc", 0) or 0
        try:
            price = float(price_raw)
        except (ValueError, TypeError):
            price = 0.0

        program = {
            "date": date_str,
            "time": goods.get("beTime", "未知"),
            "name": goods.get("goodsNm", "未知商品"),
            "sn": goods.get("goodsSn", ""),
            "price": price,
            "price_formatted": f"¥{price:.2f}" if price else "价格待定",
            "market_price": goods.get("marketPrc", ""),
            "pay_tips": goods.get("payTips", "") or "",
            "sale_qty": goods.get("saleQty", ""),
            "status": str(goods.get("status", "-1")),
            "status_text": STATUS_MAP.get(str(goods.get("status", "-1")), "⚪ 未知"),
            "image_url": goods.get("imgUrl", ""),
        }
        programs.append(program)

    return programs


def generate_date_list(start_date: str, end_date: str) -> list[str]:
    """
    生成日期列表（包含起止日期，按升序排列）。

    Args:
        start_date: 起始日期，YYYYMMDD
        end_date: 结束日期，YYYYMMDD

    Returns:
        日期字符串列表
    """
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    return dates


def fetch_all_programs(date_list: list[str], area_cd: str) -> list[dict]:
    """
    批量爬取多日节目表。

    Args:
        date_list: 日期字符串列表（YYYYMMDD）
        area_cd: 区域代码

    Returns:
        所有日期的节目列表（已按日期升序排列）
    """
    all_programs = []
    total = len(date_list)
    success_count = 0
    fail_dates = []

    for i, date_str in enumerate(date_list, 1):
        try:
            print(f"  [{i}/{total}] 正在获取 {date_str} ...", end=" ", flush=True)
            raw_data = fetch_program_list(date_str, area_cd)
            programs = parse_programs(raw_data, date_str)
            all_programs.extend(programs)
            success_count += 1
            print(f"✅ {len(programs)} 个节目")
        except Exception as e:
            print(f"❌ 失败: {e}")
            fail_dates.append(date_str)

        # 请求间隔，避免过于频繁
        if i < total:
            time.sleep(REQUEST_INTERVAL)

    # 汇总信息
    print(f"\n{'=' * 60}")
    print(f"  📊 爬取完成: 成功 {success_count}/{total} 天", end="")
    if fail_dates:
        print(f"，失败日期: {', '.join(fail_dates)}", end="")
    print(f"\n  📦 共获取 {len(all_programs)} 条节目记录")
    print(f"{'=' * 60}")

    return all_programs


def format_output_multi(all_programs: list[dict], area_cd: str) -> str:
    """
    将多日节目列表格式化为可读的文本输出，按日期分组。

    Args:
        all_programs: 所有节目列表（已含 date 字段）
        area_cd: 区域代码

    Returns:
        格式化的字符串
    """
    area_name = AREA_MAP.get(area_cd, "未知区域")

    # 按日期分组
    from collections import OrderedDict
    grouped = OrderedDict()
    for p in all_programs:
        grouped.setdefault(p["date"], []).append(p)

    lines = []
    lines.append("=" * 60)
    lines.append(f"  📺 快乐购（好享购物）节目表（全量）")
    lines.append(f"  📍 {area_name}")
    lines.append(f"  📅 日期范围: {list(grouped.keys())[0]} ~ {list(grouped.keys())[-1]}")
    lines.append(f"  📊 共 {len(grouped)} 天，{len(all_programs)} 条节目")
    lines.append("=" * 60)

    for date_str, programs in grouped.items():
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            date_display = date_obj.strftime("%Y年%m月%d日")
            weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
        except ValueError:
            date_display = date_str
            weekday = ""

        lines.append(f"\n{'━' * 60}")
        lines.append(f"  📅 {date_display} {weekday}（{len(programs)} 个节目）")
        lines.append(f"{'━' * 60}")

        for i, p in enumerate(programs, 1):
            lines.append(f"\n  {'─' * 46}")
            lines.append(f"  [{i:>2}] {p['status_text']}")
            lines.append(f"  ⏰ 时间: {p['time']}")
            lines.append(f"  📦 商品: {p['name']}")
            lines.append(f"  💰 价格: {p['price_formatted']}")
            if p['pay_tips']:
                lines.append(f"  🏷️  优惠: {p['pay_tips']}")
            if p['sn']:
                lines.append(f"  🔖 编号: {p['sn']}")

    lines.append(f"\n{'=' * 60}")
    return "\n".join(lines)


def export_csv(all_programs: list[dict], filename: str):
    """
    将多日节目列表导出为 CSV 文件，按日期升序排列。

    Args:
        all_programs: 所有节目列表（已含 date 字段）
        filename: 输出文件名
    """
    if not all_programs:
        print("⚠️  无节目数据，跳过 CSV 导出")
        return

    fieldnames = [
        "日期", "时间段", "商品名称", "商品编号",
        "销售价格", "市场价", "支付优惠", "已售数量",
        "直播状态", "商品图片URL",
    ]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)

        for p in all_programs:
            writer.writerow([
                p["date"],
                p["time"],
                p["name"],
                p["sn"],
                p["price_formatted"],
                p["market_price"],
                p["pay_tips"],
                p["sale_qty"],
                p["status_text"],
                p["image_url"],
            ])

    print(f"✅ 节目表已导出至: {filename}")


def export_json(all_programs: list[dict], filename: str):
    """
    将多日节目列表导出为 JSON 文件。

    Args:
        all_programs: 所有节目列表
        filename: 输出文件名
    """
    if not all_programs:
        print("⚠️  无节目数据，跳过 JSON 导出")
        return

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_programs, f, ensure_ascii=False, indent=2)

    print(f"✅ 节目表已导出至: {filename}")


# ==================== 主函数 ====================


def main():
    parser = argparse.ArgumentParser(
        description="快乐购（好享购物）每日节目表爬虫（支持全量多日爬取）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python happigo_scraper.py                                # 最近7天节目表（默认）
  python happigo_scraper.py --days 30                      # 最近30天节目表
  python happigo_scraper.py --date 20260423                # 指定单日节目表
  python happigo_scraper.py --start 20260401 --end 20260424 # 指定日期范围
  python happigo_scraper.py --area 03                      # 省外节目表
  python happigo_scraper.py --csv output.csv               # 导出为 CSV
  python happigo_scraper.py --json-output result.json      # 导出为 JSON
        """,
    )

    # 日期参数组（互斥）
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="查询单个日期，格式 YYYYMMDD",
    )
    date_group.add_argument(
        "--start",
        type=str,
        default=None,
        help="起始日期，格式 YYYYMMDD（需配合 --end 使用）",
    )
    date_group.add_argument(
        "--days",
        type=int,
        default=7,
        help="爬取最近 N 天的节目表（默认：7）",
    )

    parser.add_argument(
        "--end", "-e",
        type=str,
        default=None,
        help="结束日期，格式 YYYYMMDD（需配合 --start 使用）",
    )
    parser.add_argument(
        "--area", "-a",
        type=str,
        choices=["02", "03"],
        default="02",
        help="区域代码：02=省内（默认），03=省外",
    )
    parser.add_argument(
        "--csv", "-c",
        type=str,
        default=None,
        metavar="FILE",
        help="导出节目表到 CSV 文件",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        metavar="FILE",
        help="导出节目表到 JSON 文件",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        default=False,
        help="在终端输出原始 JSON 数据（仅单日模式）",
    )

    args = parser.parse_args()

    # ==================== 构建日期列表 ====================

    if args.date:
        # 单日模式
        try:
            datetime.strptime(args.date, "%Y%m%d")
        except ValueError:
            print(f"❌ 日期格式错误: {args.date}，请使用 YYYYMMDD 格式")
            sys.exit(1)
        date_list = [args.date]
        mode = "single"

    elif args.start and args.end:
        # 自定义范围模式
        try:
            datetime.strptime(args.start, "%Y%m%d")
            datetime.strptime(args.end, "%Y%m%d")
        except ValueError:
            print(f"❌ 日期格式错误，请使用 YYYYMMDD 格式")
            sys.exit(1)
        if args.start > args.end:
            print(f"❌ 起始日期 {args.start} 不能晚于结束日期 {args.end}")
            sys.exit(1)
        date_list = generate_date_list(args.start, args.end)
        mode = "batch"

    else:
        # 默认：最近 N 天模式
        today = datetime.now()
        end_date = today.strftime("%Y%m%d")
        start_date = (today - timedelta(days=args.days - 1)).strftime("%Y%m%d")
        date_list = generate_date_list(start_date, end_date)
        mode = "batch"

    area_name = AREA_MAP.get(args.area, "未知区域")

    if mode == "single":
        # ==================== 单日模式 ====================
        date_str = date_list[0]
        print(f"🔍 正在获取 {date_str} 的节目表（{area_name}）...")

        try:
            raw_data = fetch_program_list(date_str, args.area)
            all_programs = parse_programs(raw_data, date_str)

            if args.json:
                print(json.dumps(raw_data, ensure_ascii=False, indent=2))
            else:
                output = format_output_multi(all_programs, args.area)
                print(output)

            if args.csv:
                export_csv(all_programs, args.csv)
            if args.json_output:
                export_json(all_programs, args.json_output)

        except requests.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"❌ 数据解析失败: {e}")
            sys.exit(1)

    else:
        # ==================== 批量模式 ====================
        print(f"🔍 开始批量爬取节目表（{area_name}）")
        print(f"  📅 日期范围: {date_list[0]} ~ {date_list[-1]}，共 {len(date_list)} 天\n")

        try:
            all_programs = fetch_all_programs(date_list, args.area)

            if not args.json:
                output = format_output_multi(all_programs, args.area)
                print(output)

            if args.csv:
                export_csv(all_programs, args.csv)
            if args.json_output:
                export_json(all_programs, args.json_output)

        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断爬取，已获取的数据将尝试导出")
            if args.csv and all_programs:
                export_csv(all_programs, args.csv)
            if args.json_output and all_programs:
                export_json(all_programs, args.json_output)
            sys.exit(1)


if __name__ == "__main__":
    main()
