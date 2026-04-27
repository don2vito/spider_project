#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环球购物（聚鲨环球精选）节目表爬虫
===================================
通过逆向分析 wp.sharkshopping.com 的前端API接口，获取每日电视购物节目表信息。

API基础地址: https://api.sharkshopping.com/ec/api
签名机制: 双重MD5签名 (MD5(MD5(拼接字符串).upper() + 密钥).upper())

用法:
    python shark_shopping_spider.py                  # 获取今日节目表
    python shark_shopping_spider.py --date 2026-04-25  # 获取指定日期节目表
    python shark_shopping_spider.py --date-range 2026-04-20 2026-04-25  # 获取日期范围
    python shark_shopping_spider.py --available-dates  # 查看可查询日期列表
    python shark_shopping_spider.py --export csv       # 导出为CSV文件
    python shark_shopping_spider.py --export json      # 导出为JSON文件
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

# ============================================================
# 常量配置
# ============================================================

# API基础地址
API_BASE_URL = "https://api.sharkshopping.com/ec/api"

# 生产环境签名密钥（从 wp.sharkshopping.com 前端JS逆向获取）
SECRET_KEY = "e662633040d6a433d48580a38fcedc49c9ba5d015dccf701096abade0c623163"

# 默认请求参数
DEFAULT_PARAMS = {
    "appid": "webapp",
    "token": "",
    "version": "4.4.1",
    "source": "wap",
    "city_num": "310100",  # 上海
    "oriSource": "wap",
}

# 请求头（模拟浏览器）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://wp.sharkshopping.com/programs_list",
    "Origin": "https://wp.sharkshopping.com",
}

# 东八区时区
CST = timezone(timedelta(hours=8))


# ============================================================
# 签名模块
# ============================================================

def md5_sign(text: str) -> str:
    """计算MD5哈希值（小写32位十六进制）"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def generate_sign(params: dict) -> str:
    """
    生成API请求签名

    签名算法（从前端JS逆向）:
    1. 过滤掉值为 None、空列表 的参数
    2. 将参数按 key 的 ASCII 升序排序
    3. 按 key+value 依次拼接成字符串（Object类型用JSON序列化）
    4. sign = MD5( MD5(拼接字符串).upper() + SECRET_KEY ).upper()

    Args:
        params: 请求参数字典（不含sign）

    Returns:
        32位大写MD5签名字符串
    """
    # 过滤并排序参数
    sorted_keys = sorted(params.keys())
    concat_str = ""

    for key in sorted_keys:
        value = params[key]
        # 跳过 None 和 list 类型的值
        if value is None or isinstance(value, list):
            continue
        # Object类型用JSON序列化
        if isinstance(value, dict):
            value = json.dumps(value, separators=(",", ":"))
        concat_str += str(key) + str(value)

    # 双重MD5签名
    first_md5 = md5_sign(concat_str).upper()
    final_sign = md5_sign(first_md5 + SECRET_KEY).upper()

    return final_sign


def build_request_params(method: str, **extra_params) -> dict:
    """
    构建完整的API请求参数（含签名）

    Args:
        method: API方法名（如 tv.program.data）
        **extra_params: 额外的请求参数

    Returns:
        包含签名的完整请求参数字典
    """
    params = {**DEFAULT_PARAMS, **extra_params}
    params["timestamp"] = str(int(time.time() * 1000))
    params["method"] = method
    sign = generate_sign(params)
    params["sign"] = sign
    return params


# ============================================================
# API请求模块
# ============================================================

def make_api_request(method: str, **extra_params) -> dict:
    """
    发送API请求

    Args:
        method: API方法名
        **extra_params: 额外参数

    Returns:
        API响应的JSON数据
    """
    params = build_request_params(method, **extra_params)
    # method 参数放在 URL 路径中，不在 query params 中
    url = f"{API_BASE_URL}?method={method}"
    query_params = {k: v for k, v in params.items() if k != "method"}

    try:
        response = requests.get(url, params=query_params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("rsp") != "succ":
            print(f"[警告] API返回异常: {data.get('res', '未知错误')}", file=sys.stderr)
            return {}

        return data.get("data", {}).get("returndata", {})

    except requests.RequestException as e:
        print(f"[错误] 请求失败: {e}", file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(f"[错误] JSON解析失败: {e}", file=sys.stderr)
        return {}


def get_available_dates() -> list:
    """获取可查询的日期列表"""
    data = make_api_request("tv.program.date")
    if isinstance(data, list):
        return data
    return []


def get_program_categories() -> list:
    """获取节目分类列表"""
    data = make_api_request("tv.program.categories")
    if isinstance(data, list):
        return data
    return []


def get_program_data(date: str, cat_id: str = "", brand_id: str = "") -> dict:
    """
    获取指定日期的节目数据

    Args:
        date: 查询日期 (YYYY-MM-DD格式)
        cat_id: 分类ID（可选）
        brand_id: 品牌ID（可选）

    Returns:
        包含频道信息和节目数据的字典
    """
    params = {"date": date}
    if cat_id:
        params["cat_id"] = cat_id
    if brand_id:
        params["brand_id"] = brand_id

    return make_api_request("tv.program.data", **params)


# ============================================================
# 数据解析模块
# ============================================================

def timestamp_to_time_str(ts: int) -> str:
    """将Unix时间戳转换为 HH:MM 格式（东八区）"""
    if ts <= 0:
        return "--:--"
    dt = datetime.fromtimestamp(ts, tz=CST)
    return dt.strftime("%H:%M")


def parse_program_item(item: dict) -> dict:
    """
    解析单个节目条目

    Args:
        item: API返回的单个节目数据

    Returns:
        解析后的节目信息字典
    """
    goods = item.get("goods") or {}

    # 提取优惠信息
    discount_info = ""
    jz_label = goods.get("jz_label")
    discount_label = goods.get("discount_label")
    if jz_label:
        discount_info = jz_label.get("labelName", "")
    elif discount_label:
        discount_info = discount_label.get("labelName", "")
    if not discount_info:
        discount_info = goods.get("description", "")

    # 提取价格前缀
    price_pre = goods.get("price_pre", "")
    price_mobile = goods.get("price_mobile", "")

    return {
        "日期": item.get("real_date", ""),
        "显示日期": item.get("show_date", ""),
        "开始时间": timestamp_to_time_str(item.get("start_time", 0)),
        "结束时间": timestamp_to_time_str(item.get("end_time", 0)),
        "分类": item.get("cat_name", ""),
        "品牌": item.get("brand_name", ""),
        "商品名称": goods.get("name", ""),
        "SKU": goods.get("sku", ""),
        "手机价": goods.get("price", ""),
        "市场价": goods.get("marketprice", ""),
        "价格前缀": price_pre,
        "手机价前缀": price_mobile,
        "优惠信息": discount_info,
        "商品链接": goods.get("wapUrl", ""),
        "商品图片": goods.get("image", ""),
        "一级分类": goods.get("product_first", ""),
        "二级分类": goods.get("product_second", ""),
        "三级分类": goods.get("product_third", ""),
    }


def parse_program_list(raw_data: dict) -> tuple:
    """
    解析完整的节目数据

    Args:
        raw_data: API返回的完整数据

    Returns:
        (频道信息, 节目列表)
    """
    channel = raw_data.get("channel", {})
    program_data = raw_data.get("program_data", [])

    programs = []
    for item in program_data:
        if item.get("goods") is not None:
            programs.append(parse_program_item(item))

    return channel, programs


# ============================================================
# 数据输出模块
# ============================================================

def print_table(channel: dict, programs: list):
    """在控制台以表格形式打印节目表"""
    channel_name = channel.get("channel_name", "聚鲨环球精选")

    if not programs:
        print(f"\n📺 {channel_name} - 暂无节目数据\n")
        return

    # 表格列定义
    columns = ["开始时间", "结束时间", "分类", "商品名称", "手机价", "优惠信息"]
    col_widths = [8, 8, 10, 32, 8, 10]

    # 计算分隔线
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    # 表头
    header = "|" + "|".join(f" {col:<{w}} " for col, w in zip(columns, col_widths)) + "|"

    print(f"\n📺 {channel_name} - 节目表 ({programs[0]['日期']})")
    print(f"   共 {len(programs)} 个节目")
    print(separator)
    print(header)
    print(separator)

    for prog in programs:
        # 截断过长的字段
        name = prog["商品名称"][:30] + ".." if len(prog["商品名称"]) > 30 else prog["商品名称"]
        cat = prog["分类"][:8] + ".." if len(prog["分类"]) > 8 else prog["分类"]
        discount = prog["优惠信息"][:8] + ".." if len(prog["优惠信息"]) > 8 else prog["优惠信息"]

        row_data = [
            prog["开始时间"],
            prog["结束时间"],
            cat,
            name,
            f"¥{prog['手机价']}",
            discount,
        ]
        row = "|" + "|".join(f" {val:<{w}} " for val, w in zip(row_data, col_widths)) + "|"
        print(row)

    print(separator)
    print()


def print_available_dates(dates: list):
    """打印可查询日期列表"""
    print("\n📅 可查询日期列表:")
    print("-" * 40)
    for d in dates:
        marker = " ← 今日" if d.get("show_date") == "今日" else ""
        print(f"  {d['show_date']:>6s}  ({d['real_date']}){marker}")
    print("-" * 40)
    print()


def print_categories(categories: list):
    """打印节目分类列表"""
    print("\n📂 节目分类列表:")
    print("-" * 50)
    for cat in categories:
        brands = [b["brand_name"] for b in cat.get("brand_list", [])]
        print(f"  [{cat['cat_id']}] {cat['cat_name']}")
        if brands:
            print(f"       品牌: {', '.join(brands[:5])}{'...' if len(brands) > 5 else ''}")
    print("-" * 50)
    print()


def export_to_csv(programs: list, filename: str = None):
    """导出节目数据为CSV文件"""
    if not programs:
        print("[警告] 无数据可导出", file=sys.stderr)
        return

    if filename is None:
        date_str = programs[0]["日期"]
        filename = f"shark_shopping_{date_str}.csv"

    filepath = os.path.join("/workspace", filename)

    # 定义CSV列
    fieldnames = [
        "日期", "显示日期", "开始时间", "结束时间", "分类", "品牌",
        "商品名称", "SKU", "手机价", "市场价", "价格前缀", "手机价前缀", "优惠信息",
        "商品链接", "商品图片", "一级分类", "二级分类", "三级分类",
    ]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(programs)

    print(f"✅ CSV文件已保存: {filepath}")


def export_to_json(programs: list, channel: dict, filename: str = None):
    """导出节目数据为JSON文件"""
    if not programs:
        print("[警告] 无数据可导出", file=sys.stderr)
        return

    if filename is None:
        date_str = programs[0]["日期"]
        filename = f"shark_shopping_{date_str}.json"

    filepath = os.path.join("/workspace", filename)

    output = {
        "频道": channel,
        "获取时间": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"),
        "节目数量": len(programs),
        "节目列表": programs,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON文件已保存: {filepath}")


# ============================================================
# 主程序入口
# ============================================================

def fetch_single_date(date_str: str, export_format: str = None) -> tuple:
    """
    获取单个日期的节目数据

    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        export_format: 导出格式 (csv/json/None)

    Returns:
        (频道信息, 节目列表)
    """
    print(f"📡 正在获取 {date_str} 的节目数据...")
    raw_data = get_program_data(date_str)
    channel, programs = parse_program_list(raw_data)

    if programs:
        print(f"✅ 成功获取 {len(programs)} 个节目")
        print_table(channel, programs)

        if export_format == "csv":
            export_to_csv(programs)
        elif export_format == "json":
            export_to_json(programs, channel)
    else:
        print(f"⚠️  {date_str} 暂无节目数据")

    return channel, programs


def main():
    parser = argparse.ArgumentParser(
        description="环球购物（聚鲨环球精选）节目表爬虫",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                              # 获取今日节目表
  %(prog)s --date 2026-04-25            # 获取指定日期节目表
  %(prog)s --date-range 2026-04-20 2026-04-25  # 获取日期范围
  %(prog)s --available-dates            # 查看可查询日期
  %(prog)s --categories                 # 查看节目分类
  %(prog)s --date 2026-04-24 --export csv   # 导出CSV
  %(prog)s --date 2026-04-24 --export json  # 导出JSON
        """,
    )

    parser.add_argument("--date", "-d", type=str, help="查询日期 (YYYY-MM-DD格式)")
    parser.add_argument("--date-range", "-r", nargs=2, type=str, metavar=("START", "END"),
                        help="日期范围 (YYYY-MM-DD YYYY-MM-DD)")
    parser.add_argument("--available-dates", "-a", action="store_true",
                        help="查看可查询日期列表")
    parser.add_argument("--categories", "-c", action="store_true",
                        help="查看节目分类列表")
    parser.add_argument("--export", "-e", type=str, choices=["csv", "json"],
                        help="导出格式 (csv 或 json)")
    parser.add_argument("--city", type=str, default="310100",
                        help="城市编号 (默认: 310100 上海)")

    args = parser.parse_args()

    # 更新城市编号
    DEFAULT_PARAMS["city_num"] = args.city

    # 查看可查询日期
    if args.available_dates:
        dates = get_available_dates()
        if dates:
            print_available_dates(dates)
        else:
            print("❌ 获取日期列表失败")
        return

    # 查看节目分类
    if args.categories:
        categories = get_program_categories()
        if categories:
            print_categories(categories)
        else:
            print("❌ 获取分类列表失败")
        return

    # 确定查询日期
    if args.date:
        query_date = args.date
    elif args.date_range:
        start_date = datetime.strptime(args.date_range[0], "%Y-%m-%d")
        end_date = datetime.strptime(args.date_range[1], "%Y-%m-%d")
    else:
        # 默认查询今日
        query_date = datetime.now(CST).strftime("%Y-%m-%d")

    # 获取单日数据
    if args.date or (not args.date_range):
        fetch_single_date(query_date, args.export)
        return

    # 获取日期范围数据
    current = start_date
    all_results = []

    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        print(f"\n{'='*60}")
        print(f"📡 正在获取 {date_str} 的节目数据...")

        raw_data = get_program_data(date_str)
        channel, programs = parse_program_list(raw_data)

        if programs:
            print(f"✅ 成功获取 {len(programs)} 个节目")
            print_table(channel, programs)
            all_results.extend(programs)
        else:
            print(f"⚠️  {date_str} 暂无节目数据")

        current += timedelta(days=1)
        time.sleep(0.5)  # 礼貌性延迟，避免请求过快

    # 导出汇总数据
    if all_results and args.export:
        if args.export == "csv":
            export_to_csv(all_results, f"shark_shopping_{args.date_range[0]}_{args.date_range[1]}.csv")
        elif args.export == "json":
            export_to_json(all_results, {}, f"shark_shopping_{args.date_range[0]}_{args.date_range[1]}.json")

    # 汇总统计
    if all_results:
        print(f"\n{'='*60}")
        print(f"📊 汇总统计:")
        print(f"   日期范围: {args.date_range[0]} ~ {args.date_range[1]}")
        print(f"   总节目数: {len(all_results)}")
        # 统计分类分布
        cat_count = {}
        for p in all_results:
            cat = p["分类"]
            cat_count[cat] = cat_count.get(cat, 0) + 1
        print(f"   分类分布:")
        for cat, count in sorted(cat_count.items(), key=lambda x: -x[1]):
            print(f"     {cat}: {count} 个节目")


if __name__ == "__main__":
    main()
