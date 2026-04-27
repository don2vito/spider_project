#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一展会网(onezh.com) 2026年国内展会信息爬虫
功能：爬取2026年每月展会信息，按"上海"和"非上海"分类输出为Excel
"""

import re
import time
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

# ============================================================
# 配置
# ============================================================
BASE_URL = "https://www.onezh.com"
OUTPUT_FILE = "2026年展会信息.xlsx"

# 请求头
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.onezh.com/zhanhui/",
}

# 请求间隔（秒）
REQUEST_DELAY = 1.5

# 12个月的日期范围
MONTHS = [
    ("1月",  "20260101", "20260131"),
    ("2月",  "20260201", "20260228"),
    ("3月",  "20260301", "20260331"),
    ("4月",  "20260401", "20260430"),
    ("5月",  "20260501", "20260531"),
    ("6月",  "20260601", "20260630"),
    ("7月",  "20260701", "20260731"),
    ("8月",  "20260801", "20260831"),
    ("9月",  "20260901", "20260930"),
    ("10月", "20261001", "20261031"),
    ("11月", "20261101", "20261130"),
    ("12月", "20261201", "20261231"),
]

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# ============================================================
# 网络请求
# ============================================================
def create_session() -> requests.Session:
    """创建带重试机制的Session"""
    session = requests.Session()
    session.headers.update(HEADERS)
    # 重试适配器
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_page(session: requests.Session, url: str) -> str:
    """请求页面HTML，带异常处理"""
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except requests.RequestException as e:
        logger.error(f"请求失败 [{url}]: {e}")
        return ""


# ============================================================
# 页面解析
# ============================================================
def get_total_pages(soup: BeautifulSoup) -> int:
    """
    从分页区域获取总页数。
    优先从 <span>共N页</span> 提取，备选从尾页链接提取。
    """
    # 方式1：从 "共N页" 文本提取
    page_div = soup.find("div", class_="NewPage")
    if page_div:
        text = page_div.get_text()
        m = re.search(r"共(\d+)页", text)
        if m:
            return int(m.group(1))

    # 方式2：从尾页链接提取
    if page_div:
        last_links = page_div.find_all("a", string=re.compile(r"尾页"))
        if last_links:
            href = last_links[-1].get("href", "")
            m = re.search(r"/zhanhui/(\d+)_", href)
            if m:
                return int(m.group(1))

    return 1  # 默认1页


def parse_exhibition_row(row_div) -> dict:
    """
    解析单个展会条目 <div class='row'>
    返回字典：展会名称、详情链接、展会时间、展馆名称、面积、参商、观众、简介
    """
    info = {
        "展会名称": "",
        "详情链接": "",
        "展会时间": "",
        "展馆名称": "",
        "展会面积": "",
        "参商数量": "",
        "观众数量": "",
        "展会简介": "",
    }

    # 展会名称和详情链接
    strong_a = row_div.select_one("strong a")
    if strong_a:
        info["展会名称"] = strong_a.get("title", "") or strong_a.get_text(strip=True)
        href = strong_a.get("href", "")
        if href:
            info["详情链接"] = BASE_URL + href if href.startswith("/") else href

    # 面积、参商、观众
    area_div = row_div.find("div", class_="area")
    if area_div:
        info["展会面积"] = area_div.get_text(strip=True)

    people1_div = row_div.find("div", class_="people1")
    if people1_div:
        info["参商数量"] = people1_div.get_text(strip=True)

    people2_div = row_div.find("div", class_="people2")
    if people2_div:
        info["观众数量"] = people2_div.get_text(strip=True)

    # 从 <em class='cgree1'> 提取简介、时间、展馆
    em_list = row_div.find_all("em", class_="cgree1")
    if len(em_list) >= 1:
        # 第一个em通常是简介
        info["展会简介"] = em_list[0].get_text(strip=True)

    if len(em_list) >= 2:
        # 第二个em通常包含时间和展馆
        detail_text = em_list[-1].get_text(strip=True)
        # 提取展会时间
        time_match = re.search(r"展会时间：(.+?)(?:\s|$)", detail_text)
        if time_match:
            info["展会时间"] = time_match.group(1).strip()
        # 提取展馆名称
        venue_match = re.search(r"展馆：(.+)", detail_text)
        if venue_match:
            info["展馆名称"] = venue_match.group(1).strip()

    return info


def parse_page(html: str) -> tuple[list[dict], int]:
    """
    解析一个列表页，返回 (展会列表, 总页数)
    """
    soup = BeautifulSoup(html, "html.parser")
    exhibitions = []
    total_pages = get_total_pages(soup)

    # 查找所有展会条目
    row_divs = soup.find_all("div", class_="row")
    for row in row_divs:
        # 确保该row包含展会链接（排除广告等）
        if row.select_one("strong a"):
            info = parse_exhibition_row(row)
            if info["展会名称"]:
                exhibitions.append(info)

    return exhibitions, total_pages


# ============================================================
# 主爬虫逻辑
# ============================================================
def crawl_month(session: requests.Session, month_name: str, start_date: str, end_date: str) -> list[dict]:
    """爬取某个月份的所有展会（自动翻页）"""
    all_exhibitions = []
    base_path = f"/zhanhui/{{page}}_0_0_0_{start_date}/{end_date}/"

    # 请求第1页
    url = BASE_URL + base_path.format(page=1)
    logger.info(f"  正在爬取 {month_name} 第1页: {url}")
    html = fetch_page(session, url)
    if not html:
        logger.warning(f"  {month_name} 第1页获取失败，跳过")
        return all_exhibitions

    exhibitions, total_pages = parse_page(html)
    all_exhibitions.extend(exhibitions)
    logger.info(f"  {month_name} 共 {total_pages} 页，第1页获取 {len(exhibitions)} 条展会")

    # 爬取剩余页
    for page in range(2, total_pages + 1):
        time.sleep(REQUEST_DELAY)
        url = BASE_URL + base_path.format(page=page)
        logger.info(f"  正在爬取 {month_name} 第{page}/{total_pages}页")
        html = fetch_page(session, url)
        if not html:
            logger.warning(f"  {month_name} 第{page}页获取失败，跳过")
            continue
        exhibitions, _ = parse_page(html)
        all_exhibitions.extend(exhibitions)
        logger.info(f"  {month_name} 第{page}页获取 {len(exhibitions)} 条展会")

    return all_exhibitions


def is_shanghai(venue: str) -> bool:
    """判断展馆是否在上海"""
    if not venue:
        return False
    return "上海" in venue


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("第一展会网 2026年展会信息爬虫")
    logger.info("=" * 60)

    session = create_session()
    all_data = []

    for month_name, start_date, end_date in MONTHS:
        logger.info(f"\n>>> 开始爬取 {month_name} ({start_date} ~ {end_date})")
        exhibitions = crawl_month(session, month_name, start_date, end_date)

        for item in exhibitions:
            item["月份"] = month_name
            item["是否上海"] = "是" if is_shanghai(item["展馆名称"]) else "否"

        all_data.extend(exhibitions)
        logger.info(f"  {month_name} 共获取 {len(exhibitions)} 条展会")

        # 月份间稍长延迟
        if month_name != MONTHS[-1][0]:
            time.sleep(REQUEST_DELAY)

    logger.info(f"\n爬取完成！共获取 {len(all_data)} 条展会信息")

    if not all_data:
        logger.warning("未获取到任何展会数据，请检查网络连接")
        return

    # 整理DataFrame列顺序
    columns = [
        "月份", "是否上海", "展会名称", "展会时间", "展馆名称",
        "展会面积", "参商数量", "观众数量", "展会简介", "详情链接",
    ]
    df = pd.DataFrame(all_data, columns=columns)

    # 按上海/非上海分类
    df_shanghai = df[df["是否上海"] == "是"].reset_index(drop=True)
    df_other = df[df["是否上海"] == "否"].reset_index(drop=True)

    # 导出Excel
    output_path = OUTPUT_FILE
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_shanghai.to_excel(writer, sheet_name="上海展会", index=False)
        df_other.to_excel(writer, sheet_name="非上海展会", index=False)

        # 调整列宽
        for sheet_name in ["上海展会", "非上海展会"]:
            ws = writer.sheets[sheet_name]
            col_widths = {
                "A": 8,   # 月份
                "B": 10,  # 是否上海
                "C": 50,  # 展会名称
                "D": 30,  # 展会时间
                "E": 30,  # 展馆名称
                "F": 15,  # 展会面积
                "G": 12,  # 参商数量
                "H": 12,  # 观众数量
                "I": 60,  # 展会简介
                "J": 45,  # 详情链接
            }
            for col_letter, width in col_widths.items():
                ws.column_dimensions[col_letter].width = width

    logger.info(f"\n数据已保存至: {output_path}")
    logger.info(f"  上海展会: {len(df_shanghai)} 条")
    logger.info(f"  非上海展会: {len(df_other)} 条")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
