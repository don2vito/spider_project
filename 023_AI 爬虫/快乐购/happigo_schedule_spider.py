#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快乐购(TV5)每日节目表爬虫
========================
目标网站: https://www.happigo.com/tv5/
数据来源: AJAX API接口 (动态加载)

用法:
    python happigo_schedule_spider.py                              # 获取页面展示的7天节目表（默认）
    python happigo_schedule_spider.py --start 20260418 --end 20260424  # 指定日期范围
    python happigo_schedule_spider.py --date 20260425              # 获取单天
    python happigo_schedule_spider.py --output csv                 # 输出为CSV文件
    python happigo_schedule_spider.py --output json                # 输出为JSON文件
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

# ==================== 配置 ====================

API_URL = "https://www.happigo.com/tv5/index.php?act=tv_live&op=ajaxTvzhiboGoods"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.happigo.com/tv5/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

# 直播状态映射
LIVE_STATE_MAP = {
    0: "即将播出",
    1: "正在直播",
    2: "已结束",
}

# CSV 输出字段
CSV_FIELDS = [
    "日期", "序号", "播出时间", "商品名称", "商品ID", "销售价", "市场价",
    "商品描述", "一级分类", "二级分类", "累计销量", "库存",
    "直播状态", "商品链接", "商品图片",
]


# ==================== 核心功能 ====================


def fetch_schedule(date_str: str) -> dict:
    """
    请求API获取指定日期的节目表数据。

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，如 "20260424"

    Returns:
        API返回的JSON字典

    Raises:
        requests.RequestException: 网络请求失败
        ValueError: API返回错误或数据解析失败
    """
    params = {
        "token": "ok",
        "type": "info",
        "ymd": date_str,
    }

    print(f"[*] 正在请求 {date_str} 的节目表数据...")
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
    response.raise_for_status()

    data = response.json()

    if data.get("state") != 1:
        raise ValueError(f"API返回错误: {data.get('msg', '未知错误')}")

    goods_list = data.get("tvliveGoods", [])
    if not goods_list:
        print(f"[!] {date_str} 没有节目数据")

    return data


def parse_schedule(data: dict, date_str: str) -> list[dict]:
    """
    解析API返回的JSON数据，提取节目表关键字段。
    过滤掉开始时间属于前一天的跨天节目。

    Args:
        data: API返回的原始JSON字典
        date_str: 查询日期字符串，格式 YYYYMMDD

    Returns:
        解析后的节目条目列表，每个条目为字典
    """
    goods_list = data.get("tvliveGoods", [])
    parsed = []

    utc8 = timezone(timedelta(hours=8))

    for idx, item in enumerate(goods_list, start=1):
        # 过滤跨天节目：使用 tvStartTime 时间戳转为北京时间(UTC+8)后判断日期
        tv_start_ts = item.get("tvStartTime", "")
        if not tv_start_ts:
            continue
        ts_date = datetime.fromtimestamp(int(tv_start_ts), tz=utc8).strftime("%Y%m%d")
        if ts_date != date_str:
            continue

        entry = {
            "日期": date_str,
            "序号": idx,
            "播出时间": item.get("bochushijian", ""),
            "开始时间": item.get("tvStartTime1", ""),
            "结束时间": item.get("tvEndTime1", ""),
            "商品名称": item.get("goodsName", item.get("tvName", "")),
            "商品ID": item.get("goodsCommonid", ""),
            "销售价": item.get("salePrice", ""),
            "市场价": item.get("marketPrice", ""),
            "商品描述": item.get("goodsShortDesc2", ""),
            "一级分类": item.get("gcName1", ""),
            "二级分类": item.get("gcName2", ""),
            "累计销量": item.get("saleCounDisplay", ""),
            "库存": item.get("goodStorage", ""),
            "直播状态": LIVE_STATE_MAP.get(item.get("liveState", -1), "未知"),
            "商品链接": item.get("url", ""),
            "商品图片": item.get("pic", ""),
            "详情图片": item.get("detailPic", ""),
            "节目名称": item.get("progName", ""),
        }
        parsed.append(entry)

    # 过滤后重新编号
    for i, entry in enumerate(parsed, start=1):
        entry["序号"] = i

    return parsed


def print_schedule_table(all_data: list[dict]) -> None:
    """
    以表格形式打印全量节目表到控制台，按日期分组，日期升序排列。

    Args:
        all_data: 所有日期的节目条目列表（已按日期升序排列）
    """
    if not all_data:
        print("[!] 没有节目数据")
        return

    # 按日期分组
    from itertools import groupby
    grouped = {}
    for item in all_data:
        d = item["日期"]
        grouped.setdefault(d, []).append(item)

    total = len(all_data)
    dates = sorted(grouped.keys())
    print(f"\n{'#'*90}")
    print(f"  快乐购(TV5) 全量节目表  ({dates[0]} ~ {dates[-1]})  共 {len(dates)} 天 / {total} 个节目")
    print(f"{'#'*90}")

    for date_str in dates:
        items = grouped[date_str]
        try:
            date_display = datetime.strptime(date_str, "%Y%m%d").strftime("%Y年%m月%d日")
        except ValueError:
            date_display = date_str

        print(f"\n{'='*90}")
        print(f"  {date_display}  (共 {len(items)} 个节目)")
        print(f"{'='*90}")
        print(f"{'序号':>4}  {'播出时间':<12} {'商品名称':<30} {'销售价':>6} {'市场价':>6}  {'分类':<16} {'状态':<8}")
        print(f"{'-'*90}")

        for item in items:
            name = item["商品名称"]
            if len(name) > 28:
                name = name[:26] + ".."
            category = f"{item['一级分类']}/{item['二级分类']}"
            if len(category) > 14:
                category = category[:12] + ".."
            print(
                f"{item['序号']:>4}  {item['播出时间']:<12} {name:<30} "
                f"¥{item['销售价']:>5} ¥{item['市场价']:>5}  {category:<16} {item['直播状态']:<8}"
            )

    print(f"\n{'#'*90}\n")


def save_to_csv(all_data: list[dict], output_dir: str = ".") -> str:
    """
    将全量节目表保存为一个CSV文件，按日期升序排列。

    Args:
        all_data: 所有日期的节目条目列表
        output_dir: 输出目录

    Returns:
        保存的文件路径
    """
    if not all_data:
        print("[!] 没有数据可保存")
        return ""

    os.makedirs(output_dir, exist_ok=True)
    dates = sorted(set(item["日期"] for item in all_data))
    filepath = os.path.join(output_dir, f"happigo_schedule_{dates[0]}_{dates[-1]}.csv")

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_data)

    print(f"[✓] CSV文件已保存: {filepath}  (共 {len(all_data)} 条记录)")
    return filepath


def save_to_json(all_data: list[dict], output_dir: str = ".") -> str:
    """
    将全量节目表保存为一个JSON文件，按日期升序排列。

    Args:
        all_data: 所有日期的节目条目列表
        output_dir: 输出目录

    Returns:
        保存的文件路径
    """
    if not all_data:
        print("[!] 没有数据可保存")
        return ""

    os.makedirs(output_dir, exist_ok=True)
    dates = sorted(set(item["日期"] for item in all_data))
    filepath = os.path.join(output_dir, f"happigo_schedule_{dates[0]}_{dates[-1]}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"[✓] JSON文件已保存: {filepath}  (共 {len(all_data)} 条记录)")
    return filepath


# ==================== 主入口 ====================


def main():
    parser = argparse.ArgumentParser(
        description="快乐购(TV5)每日节目表爬虫 — 全量爬取页面展示的节目表",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python happigo_schedule_spider.py                                    # 爬取页面展示的7天节目表
  python happigo_schedule_spider.py --start 20260418 --end 20260424   # 指定日期范围
  python happigo_schedule_spider.py --date 20260425                   # 获取单天
  python happigo_schedule_spider.py --output csv                      # 导出CSV
  python happigo_schedule_spider.py --output json                     # 导出JSON
        """,
    )
    parser.add_argument(
        "--date", type=str, default=None,
        help="获取单天节目表，格式 YYYYMMDD（与 --start/--end 互斥）",
    )
    parser.add_argument(
        "--start", type=str, default=None,
        help="起始日期，格式 YYYYMMDD（默认：今天往前推6天）",
    )
    parser.add_argument(
        "--end", type=str, default=None,
        help="结束日期，格式 YYYYMMDD（默认：今天）",
    )
    parser.add_argument(
        "--output", type=str, default="table",
        choices=["table", "csv", "json", "all"],
        help="输出格式：table(表格打印)/csv/json/all(全部)（默认：table）",
    )
    parser.add_argument(
        "--output-dir", type=str, default=".",
        help="文件输出目录（默认：当前目录）",
    )

    args = parser.parse_args()

    # 确定日期范围
    if args.date:
        # 单天模式
        start_date = datetime.strptime(args.date, "%Y%m%d")
        end_date = start_date
    elif args.start or args.end:
        # 自定义范围模式
        start_date = datetime.strptime(args.start, "%Y%m%d") if args.start else datetime.now() - timedelta(days=6)
        end_date = datetime.strptime(args.end, "%Y%m%d") if args.end else datetime.now()
    else:
        # 默认：页面展示的7天范围（今天往前推6天 ~ 今天）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6)

    # 生成日期列表（升序）
    date_list = []
    current = start_date
    while current <= end_date:
        date_list.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)

    print(f"[*] 爬取日期范围: {date_list[0]} ~ {date_list[-1]}，共 {len(date_list)} 天\n")

    # 全量数据收集（按日期升序）
    all_data = []

    for date_str in date_list:
        try:
            # 1. 请求数据
            raw_data = fetch_schedule(date_str)

            # 2. 解析数据（过滤跨天节目）
            parsed = parse_schedule(raw_data, date_str)

            if not parsed:
                continue

            all_data.extend(parsed)

            # 请求间隔，避免过快
            if len(date_list) > 1:
                time.sleep(0.5)

        except requests.RequestException as e:
            print(f"[✗] 网络请求失败 ({date_str}): {e}")
        except ValueError as e:
            print(f"[✗] 数据解析失败 ({date_str}): {e}")
        except Exception as e:
            print(f"[✗] 未知错误 ({date_str}): {e}")

    # 输出结果
    if not all_data:
        print("[!] 未获取到任何节目数据")
        sys.exit(1)

    print(f"\n[*] 数据获取完成，共 {len(all_data)} 个节目")

    if args.output in ("table", "all"):
        print_schedule_table(all_data)

    if args.output in ("csv", "all"):
        save_to_csv(all_data, args.output_dir)

    if args.output in ("json", "all"):
        save_to_json(all_data, args.output_dir)


if __name__ == "__main__":
    main()
