#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海市统计局数据抓取代理服务器
Flask backend for scraping tjj.sh.gov.cn statistical data
"""

from flask import Flask, request, jsonify, Response, send_file, send_from_directory
from flask_cors import CORS
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urljoin
import time
import re
import io

app = Flask(__name__)
CORS(app)

BASE_URL = "https://tjj.sh.gov.cn"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# ── 内存缓存 ──
_cache = {}
CACHE_TTL = 600  # 10 分钟


def fetch_html(url, timeout=15):
    """带缓存和限速的 HTML 抓取"""
    now = time.time()
    if url in _cache and (now - _cache[url]["time"]) < CACHE_TTL:
        return _cache[url]["html"]
    time.sleep(0.5)
    try:
        resp = requests.get(url, timeout=timeout, headers=HEADERS)
        resp.encoding = "utf-8"
        html = resp.text
        _cache[url] = {"html": html, "time": now}
        return html
    except requests.RequestException as e:
        return None


def make_error(msg, code=500):
    return jsonify({"error": msg}), code


# ══════════════════════════════════════════════════════════════
# 端点 1: 获取年份列表
# ══════════════════════════════════════════════════════════════
def extract_js_redirect(html):
    """从 HTML 中提取 JavaScript 重定向 URL"""
    m = re.search(r'window\.location\.href\s*=\s*["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    m = re.search(r'location\.replace\s*\(\s*["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    return None


def resolve_url(url):
    """解析 URL，处理 JavaScript 重定向"""
    html = fetch_html(url)
    if not html:
        return url, None
    redirect = extract_js_redirect(html)
    if redirect:
        full_redirect = urljoin(url, redirect)
        actual_html = fetch_html(full_redirect)
        return full_redirect, actual_html
    return url, html


@app.route("/api/years")
def get_years():
    """解析首页年份下拉菜单，返回年份列表与页码映射"""
    html = fetch_html(f"{BASE_URL}/sjfb/index.html")
    if not html:
        return make_error("无法访问目标网站")

    soup = BeautifulSoup(html, "html.parser")
    years = []

    # 查找年份下拉菜单 - 实际是 <ul> 列表结构（第一个 more-years 是月度数据年份）
    more_years_divs = soup.find_all("div", class_="more-years")
    more_years_div = more_years_divs[0] if more_years_divs else None
    if more_years_div:
        for li in more_years_div.find_all("li"):
            link = li.find("a")
            if link:
                text = link.get_text(strip=True)
                href = link.get("href", "")
                title = link.get("title", "")
                # 提取年份数字
                year_num = None
                m = re.search(r"(\d{4})", text)
                if m:
                    year_num = int(m.group(1))
                elif title and re.search(r"^\d{4}$", title.strip()):
                    year_num = int(title.strip())
                if year_num:
                    full_url = urljoin(BASE_URL, href) if href else f"{BASE_URL}/sjfb/index.html"
                    years.append({"year": year_num, "url": full_url, "label": f"{year_num}年"})

    # 回退：尝试 <select> 结构
    if not years:
        select = soup.find("select")
        if select:
            for opt in select.find_all("option"):
                text = opt.get_text(strip=True)
                href = opt.get("value", "")
                m = re.search(r"(\d{4})", text)
                if m:
                    year = int(m.group(1))
                    full_url = urljoin(BASE_URL, href) if href else f"{BASE_URL}/sjfb/index.html"
                    years.append({"year": year, "url": full_url, "label": text})

    # 按年份降序排列
    years.sort(key=lambda x: x["year"], reverse=True)

    if not years:
        # 回退：硬编码已知年份
        years = [{"year": y, "url": f"{BASE_URL}/sjfb/index.html", "label": f"{y}年"}
                 for y in range(2026, 2018, -1)]

    return jsonify({"years": years})


# ══════════════════════════════════════════════════════════════
# 端点 2: 获取指定年份的指标矩阵
# ══════════════════════════════════════════════════════════════
@app.route("/api/matrix")
def get_matrix():
    """获取指定年份的完整指标矩阵表格"""
    year = request.args.get("year", type=int)
    if not year:
        return make_error("缺少 year 参数", 400)

    # 先获取年份映射
    html = fetch_html(f"{BASE_URL}/sjfb/index.html")
    if not html:
        return make_error("无法访问目标网站")

    soup = BeautifulSoup(html, "html.parser")
    year_url = None

    # 查找年份链接 - 实际是 <ul> 列表结构（第一个 more-years 是月度数据年份）
    more_years_divs = soup.find_all("div", class_="more-years")
    more_years_div = more_years_divs[0] if more_years_divs else None
    if more_years_div:
        for li in more_years_div.find_all("li"):
            link = li.find("a")
            if link:
                text = link.get_text(strip=True)
                href = link.get("href", "")
                title = link.get("title", "")
                year_num = None
                m = re.search(r"(\d{4})", text)
                if m:
                    year_num = int(m.group(1))
                elif title and re.search(r"^\d{4}$", title.strip()):
                    year_num = int(title.strip())
                if year_num == year:
                    year_url = urljoin(BASE_URL, href) if href else f"{BASE_URL}/sjfb/index.html"
                    break

    # 回退：尝试 <select> 结构
    if not year_url:
        select = soup.find("select")
        if select:
            for opt in select.find_all("option"):
                text = opt.get_text(strip=True)
                m = re.search(r"(\d{4})", text)
                if m and int(m.group(1)) == year:
                    href = opt.get("value", "")
                    year_url = urljoin(BASE_URL, href) if href else f"{BASE_URL}/sjfb/index.html"
                    break

    if not year_url:
        return make_error(f"未找到 {year} 年的数据页面", 404)

    # 解析年份页面（处理 JavaScript 重定向）
    resolved_url, matrix_html = resolve_url(year_url)
    if not matrix_html:
        return make_error(f"无法访问 {year} 年数据页面")

    matrix_soup = BeautifulSoup(matrix_html, "html.parser")

    # 找到主数据表格
    table = matrix_soup.find("table")
    if not table:
        return make_error("未找到数据表格")

    # 解析表头（月份列）
    rows = table.find_all("tr")
    if not rows:
        return make_error("表格为空")

    # 第一行是表头
    header_row = rows[0]
    header_cells = header_row.find_all(["th", "td"])
    # 跳过第一个"月份/内容"合并单元格
    period_labels = []
    for cell in header_cells[1:]:
        text = cell.get_text(strip=True)
        period_labels.append(text)

    # 解析数据行
    categories = []
    current_category = None
    current_category_order = 0

    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        if not cells:
            continue

        first_cell = cells[0]
        first_text = first_cell.get_text(strip=True)

        # 判断是否为类别标题行（如 "三、工业" 或 "二、上海市生产总值"）
        is_category_row = bool(re.match(r"^[一二三四五六七八九十]+、", first_text))
        link = first_cell.find("a")

        if is_category_row:
            current_category = first_text
            current_category_order += 1

        # 如果该行有链接，则同时作为指标行处理
        if link:
            indicator_id = extract_indicator_id(link.get("href", ""))
            if indicator_id:
                indicator = parse_indicator_row(cells, period_labels, current_category, current_category_order)
                if indicator:
                    categories.append(indicator)

    return jsonify({
        "year": year,
        "url": year_url,
        "categories": categories,
        "period_labels": period_labels
    })


def extract_indicator_id(href):
    """从链接中提取指标 ID（如 ydsj31）"""
    if not href:
        return None
    m = re.search(r"/([a-z]+\d*)/index", href)
    if m:
        return m.group(1)
    m = re.search(r"/([a-z]+\d*)/\d", href)
    if m:
        return m.group(1)
    return None


def parse_indicator_row(cells, period_labels, category, category_order):
    """解析单行指标数据"""
    first_cell = cells[0]
    link = first_cell.find("a")
    if not link:
        return None

    name = link.get_text(strip=True)
    href = link.get("href", "")
    indicator_id = extract_indicator_id(href)
    index_url = urljoin(BASE_URL, href) if href else ""

    # 判断频率
    frequency = "monthly"
    periods = {}

    for i, cell in enumerate(cells[1:]):
        if i >= len(period_labels):
            break
        label = period_labels[i]
        cell_link = cell.find("a")

        if cell_link and cell_link.get("href"):
            link_text = cell_link.get_text(strip=True)
            link_href = cell_link.get("href", "")
            full_url = urljoin(BASE_URL, link_href)

            periods[label] = {
                "label": link_text,
                "url": full_url,
                "has_data": True
            }
            # 检测季度数据
            if "季度" in label or "季度" in link_text:
                frequency = "quarterly"
        else:
            cell_text = cell.get_text(strip=True)
            if cell_text:
                periods[label] = {
                    "label": cell_text,
                    "url": None,
                    "has_data": False
                }
            else:
                periods[label] = None

    return {
        "id": indicator_id,
        "name": name,
        "category": category,
        "category_order": category_order,
        "index_url": index_url,
        "frequency": frequency,
        "periods": periods
    }


# ══════════════════════════════════════════════════════════════
# 端点 3: 获取指定指标的详情列表（含分页遍历）
# ══════════════════════════════════════════════════════════════
@app.route("/api/indicator-list")
def get_indicator_list():
    """获取指定指标的所有历史数据列表"""
    indicator_id = request.args.get("indicator_id", "").strip()
    year = request.args.get("year", type=int)

    if not indicator_id:
        return make_error("缺少 indicator_id 参数", 400)

    all_items = []
    page = 1

    while True:
        if page == 1:
            url = f"{BASE_URL}/{indicator_id}/index.html"
        else:
            url = f"{BASE_URL}/{indicator_id}/index_{page}.html"

        html = fetch_html(url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")

        # 查找列表区域
        items = parse_list_page(soup)
        if not items:
            break

        all_items.extend(items)

        # 检查是否有下一页
        has_next = False
        pagination = soup.find("div", class_="page")
        if pagination:
            next_link = pagination.find("a", string=re.compile(r"下一页"))
            if next_link:
                has_next = True
        else:
            # 尝试其他分页模式
            for a in soup.find_all("a", href=True):
                if "下一页" in a.get_text():
                    has_next = True
                    break

        if not has_next:
            break

        page += 1
        # 安全限制：最多爬取 20 页
        if page > 20:
            break

    # 按年份过滤
    if year:
        all_items = [item for item in all_items if str(year) in item.get("title", "") or str(year) in item.get("publish_date", "")]

    # 按发布日期升序排列
    all_items.sort(key=lambda x: x.get("publish_date", ""), reverse=False)

    return jsonify({
        "indicator_id": indicator_id,
        "year": year,
        "total": len(all_items),
        "items": all_items
    })


def parse_list_page(soup):
    """解析子索引列表页中的条目"""
    items = []

    # 查找列表项 - 尝试多种选择器
    list_items = soup.find_all("li")
    for li in list_items:
        link = li.find("a")
        if not link:
            continue

        href = link.get("href", "")
        if not href or "javascript" in href.lower():
            continue

        title = link.get_text(strip=True)
        if not title:
            continue

        # 提取发布日期
        publish_date = ""
        # 尝试从文本中提取日期
        date_text = li.get_text(strip=True)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_text)
        if date_match:
            publish_date = date_match.group(1)

        full_url = urljoin(BASE_URL, href)

        items.append({
            "title": title,
            "url": full_url,
            "publish_date": publish_date
        })

    # 如果没找到 li，尝试其他结构
    if not items:
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if not href or "javascript" in href.lower() or "index" in href:
                continue
            if not re.search(r"/\d{8}/", href):
                continue

            title = a.get_text(strip=True)
            if not title or len(title) < 5:
                continue

            full_url = urljoin(BASE_URL, href)

            # 查找相邻的日期文本
            publish_date = ""
            parent = a.parent
            if parent:
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", parent.get_text())
                if date_match:
                    publish_date = date_match.group(1)

            items.append({
                "title": title,
                "url": full_url,
                "publish_date": publish_date
            })

    return items


# ══════════════════════════════════════════════════════════════
# 端点 4: 获取详情页信息
# ══════════════════════════════════════════════════════════════
@app.route("/api/detail")
def get_detail():
    """获取单个详情页信息（标题、日期、xlsx链接、图片）"""
    url = request.args.get("url", "").strip()
    if not url:
        return make_error("缺少 url 参数", 400)

    # 确保 URL 是完整的
    if url.startswith("/"):
        url = urljoin(BASE_URL, url)

    html = fetch_html(url)
    if not html:
        return make_error("无法访问详情页")

    soup = BeautifulSoup(html, "html.parser")

    # 提取标题
    title = ""
    h2 = soup.find("h2")
    if h2:
        title = h2.get_text(strip=True)
    if not title:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    # 提取发布日期
    publish_date = ""
    # 尝试从页面文本中提取
    page_text = soup.get_text()
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", page_text)
    if date_match:
        publish_date = date_match.group(1)

    # 提取 xlsx/xls 下载链接
    xlsx_url = None
    xlsx_name = None
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".xls" in href.lower():
            xlsx_url = urljoin(BASE_URL, href)
            xlsx_name = a.get_text(strip=True)
            if not xlsx_name:
                xlsx_name = href.split("/")[-1]
            break

    # 提取嵌入的图片 URL
    image_url = None
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and ("doubaocdn" in src or "cmsres" in src):
            image_url = urljoin(BASE_URL, src) if not src.startswith("http") else src
            break

    # 如果没找到特定图片，取第一个有意义的图片
    if not image_url:
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src and not src.startswith("data:"):
                image_url = urljoin(BASE_URL, src) if not src.startswith("http") else src
                break

    return jsonify({
        "title": title,
        "publish_date": publish_date,
        "url": url,
        "xlsx_url": xlsx_url,
        "xlsx_name": xlsx_name,
        "image_url": image_url
    })


# ══════════════════════════════════════════════════════════════
# 端点 5: 代理下载 xlsx 文件
# ══════════════════════════════════════════════════════════════
@app.route("/api/download-xlsx")
def download_xlsx():
    """代理下载 xlsx 文件"""
    url = request.args.get("url", "").strip()
    filename = request.args.get("filename", "").strip()

    if not url:
        return make_error("缺少 url 参数", 400)

    if url.startswith("/"):
        url = urljoin(BASE_URL, url)

    filename = unquote(filename) if filename else "data.xlsx"

    try:
        resp = requests.get(url, timeout=30, headers=HEADERS, stream=True)
        resp.raise_for_status()

        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                yield chunk

        return Response(
            generate(),
            content_type=resp.headers.get("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
            }
        )
    except requests.RequestException as e:
        return make_error(f"下载失败: {str(e)}")


# ══════════════════════════════════════════════════════════════
# 端点 6: 代理转发图片
# ══════════════════════════════════════════════════════════════
@app.route("/api/proxy-image")
def proxy_image():
    """代理转发图片（应对 CDN 跨域）"""
    url = request.args.get("url", "").strip()
    if not url:
        return make_error("缺少 url 参数", 400)

    if url.startswith("/"):
        url = urljoin(BASE_URL, url)

    try:
        resp = requests.get(url, timeout=15, headers=HEADERS, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "image/png")

        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                yield chunk

        return Response(generate(), content_type=content_type)
    except requests.RequestException as e:
        return make_error(f"图片加载失败: {str(e)}")


# ══════════════════════════════════════════════════════════════
# 端点 7: 批量获取详情（用于批量下载场景）
# ══════════════════════════════════════════════════════════════
@app.route("/api/batch-details")
def batch_details():
    """批量获取多个详情页的摘要信息"""
    urls = request.args.getlist("urls")
    if not urls:
        # 也支持 JSON body
        data = request.get_json(silent=True)
        if data and "urls" in data:
            urls = data["urls"]

    if not urls:
        return make_error("缺少 urls 参数", 400)

    results = []
    for url in urls:
        if url.startswith("/"):
            url = urljoin(BASE_URL, url)

        html = fetch_html(url)
        if not html:
            results.append({"url": url, "error": "无法访问"})
            continue

        soup = BeautifulSoup(html, "html.parser")

        title = ""
        h2 = soup.find("h2")
        if h2:
            title = h2.get_text(strip=True)

        publish_date = ""
        page_text = soup.get_text()
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", page_text)
        if date_match:
            publish_date = date_match.group(1)

        xlsx_url = None
        xlsx_name = None
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".xlsx" in href.lower():
                xlsx_url = urljoin(BASE_URL, href)
                xlsx_name = a.get_text(strip=True)
                if not xlsx_name:
                    xlsx_name = href.split("/")[-1]
                break

        results.append({
            "url": url,
            "title": title,
            "publish_date": publish_date,
            "xlsx_url": xlsx_url,
            "xlsx_name": xlsx_name
        })

    return jsonify({"results": results})


# ══════════════════════════════════════════════════════════════
# XLS/XLSX 解析工具
# ══════════════════════════════════════════════════════════════
import xlrd
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill


def parse_xls_file(file_content, filename):
    """解析 xls/xlsx 文件，返回结构化数据"""
    try:
        if filename.lower().endswith(".xlsx"):
            import openpyxl as oxl
            wb = oxl.load_workbook(io.BytesIO(file_content))
            ws = wb.active
            rows = []
            for row in ws.iter_rows(values_only=True):
                rows.append([cell if cell is not None else "" for cell in row])
            return rows
        else:
            # 旧版 .xls
            wb = xlrd.open_workbook(file_contents=file_content)
            ws = wb.sheet_by_index(0)
            rows = []
            for r in range(ws.nrows):
                row_data = []
                for c in range(ws.ncols):
                    cell = ws.cell(r, c)
                    if cell.ctype == xlrd.XL_CELL_DATE:
                        try:
                            val = xlrd.xldate_as_tuple(cell.value, wb.datemode)
                            row_data.append(f"{val[0]}-{val[1]:02d}-{val[2]:02d}")
                        except:
                            row_data.append(str(cell.value))
                    elif cell.ctype == xlrd.XL_CELL_NUMBER:
                        # 避免浮点数显示问题（如 1387.99 → 1387.99, 0.4 → 0.4）
                        if cell.value == int(cell.value):
                            row_data.append(str(int(cell.value)))
                        else:
                            row_data.append(str(cell.value))
                    else:
                        row_data.append(str(cell.value))
                rows.append(row_data)
            return rows
    except Exception as e:
        return None


def find_data_block(rows):
    """从解析的行数据中提取有效数据块（跳过标题和注释）"""
    if not rows:
        return [], []

    # 找到表头行（包含"指标"关键词的行）
    header_idx = None
    for i, row in enumerate(rows):
        row_text = " ".join(str(c) for c in row)
        if "指标" in row_text and ("亿元" in row_text or "%" in row_text or "增长" in row_text):
            header_idx = i
            break

    if header_idx is None:
        # 回退：使用第3行（索引2）作为表头
        if len(rows) > 2:
            header_idx = 2
        else:
            return rows, []

    header = rows[header_idx]
    # 清理表头
    clean_header = [str(h).strip() for h in header]

    # 提取数据行（表头之后，到空行或注释行之前）
    data_rows = []
    for i in range(header_idx + 1, len(rows)):
        row = rows[i]
        # 检查是否为空行
        if all(str(c).strip() == "" for c in row):
            if data_rows:
                break  # 数据结束后遇到空行，停止
            continue
        # 检查是否为注释行（包含"统计范围"、"数据来源"、"指标解释"等关键词）
        row_text = " ".join(str(c) for c in row)
        if any(kw in row_text for kw in ["统计范围", "数据来源", "指标解释", "说明", "注：", "注:"]):
            break
        data_rows.append([str(c).strip() for c in row])

    return clean_header, data_rows


# ══════════════════════════════════════════════════════════════
# 端点 8: 批量下载并合并导出 Excel
# ══════════════════════════════════════════════════════════════
@app.route("/api/export-merged")
def export_merged():
    """批量下载各详情页的 xls 附件，解析并合并为一个 Excel 文件"""
    urls = request.args.getlist("urls")
    indicator_name = request.args.get("indicator_name", "数据")

    if not urls:
        return make_error("缺少 urls 参数", 400)

    all_sheets = []  # [(title, publish_date, header, data_rows), ...]

    for idx, url in enumerate(urls):
        if url.startswith("/"):
            url = urljoin(BASE_URL, url)

        # 1. 获取详情页，提取附件链接
        html = fetch_html(url)
        if not html:
            all_sheets.append((f"数据{idx+1}(获取失败)", "", ["错误"], [["无法访问页面"]]))
            continue

        soup = BeautifulSoup(html, "html.parser")

        # 提取标题
        title = ""
        h2 = soup.find("h2")
        if h2:
            title = h2.get_text(strip=True)
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
        if not title:
            title = f"数据{idx+1}"

        # 提取发布日期
        publish_date = ""
        page_text = soup.get_text()
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", page_text)
        if date_match:
            publish_date = date_match.group(1)

        # 提取附件链接（支持 .xls 和 .xlsx）
        attach_url = None
        attach_name = None
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".xls" in href.lower():
                attach_url = urljoin(BASE_URL, href)
                attach_name = a.get_text(strip=True)
                if not attach_name:
                    attach_name = href.split("/")[-1]
                break

        if not attach_url:
            # 没有附件，尝试从 HTML 表格解析
            table = soup.find("table")
            if table:
                header, data_rows = parse_html_table(table)
                if header:
                    all_sheets.append((title, publish_date, header, data_rows))
                    continue
            all_sheets.append((title, publish_date, ["提示"], [["该页面无可下载的附件"]]))
            continue

        # 2. 下载附件
        time.sleep(0.3)  # 限速
        try:
            resp = requests.get(attach_url, timeout=30, headers=HEADERS)
            resp.raise_for_status()
            file_content = resp.content
        except Exception as e:
            all_sheets.append((title, publish_date, ["错误"], [[f"下载失败: {str(e)}"]]))
            continue

        # 3. 解析文件
        rows = parse_xls_file(file_content, attach_name or "data.xls")
        if rows is None:
            all_sheets.append((title, publish_date, ["错误"], [["文件解析失败"]]))
            continue

        # 4. 提取数据块
        header, data_rows = find_data_block(rows)
        if not header and not data_rows:
            # 回退：使用全部行
            all_sheets.append((title, publish_date, rows[0] if rows else [], rows[1:] if len(rows) > 1 else []))
        else:
            all_sheets.append((title, publish_date, header, data_rows))

    # 5. 生成合并的 Excel 文件
    wb = Workbook()
    # 删除默认 sheet
    wb.remove(wb.active)

    # 样式定义
    title_font = Font(name="微软雅黑", bold=True, size=14, color="1F4E79")
    header_font = Font(name="微软雅黑", bold=True, size=11)
    header_fill = PatternFill(start_color="DAEEF3", end_color="DAEEF3", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    data_font = Font(name="微软雅黑", size=10)
    data_alignment = Alignment(vertical="center")
    number_alignment = Alignment(horizontal="right", vertical="center")
    link_font = Font(name="微软雅黑", size=11, color="0563C1", underline="single")
    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )
    cat_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    cat_font = Font(name="微软雅黑", bold=True, size=10)

    # ── Sheet 1: 目录 ──
    ws_toc = wb.create_sheet(title="目录")
    ws_toc.sheet_properties.tabColor = "1F4E79"

    # 标题行
    ws_toc.merge_cells("A1:D1")
    title_cell = ws_toc.cell(row=1, column=1, value=f"{indicator_name} — 全量数据目录")
    title_cell.font = title_font
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_toc.row_dimensions[1].height = 36

    # 副标题
    ws_toc.merge_cells("A2:D2")
    sub_cell = ws_toc.cell(row=2, column=1, value=f"共 {len(all_sheets)} 个数据源 · 按日期升序排列")
    sub_cell.font = Font(name="微软雅黑", size=10, color="666666")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_toc.row_dimensions[2].height = 22

    # 目录表头
    toc_headers = ["序号", "数据名称", "发布日期", "跳转链接"]
    for col_idx, h in enumerate(toc_headers, 1):
        cell = ws_toc.cell(row=4, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # 记录每个数据 sheet 的名称，用于目录链接和汇总表
    sheet_name_map = []  # [(sheet_name, title, publish_date), ...]

    for title, publish_date, header, data_rows in all_sheets:
        # Sheet 名称最多31字符，去除非法字符
        sheet_name = re.sub(r'[\\/*?:[\]]', '', title)[:31]
        # 确保名称唯一
        existing_names = [ws.title for ws in wb.worksheets]
        base_name = sheet_name
        counter = 1
        while sheet_name in existing_names:
            sheet_name = f"{base_name[:27]}_{counter}"
            counter += 1

        sheet_name_map.append((sheet_name, title, publish_date))

    # 写入目录行（带超链接跳转）
    for idx, (sheet_name, title, publish_date) in enumerate(sheet_name_map):
        row = 5 + idx
        # 序号
        c = ws_toc.cell(row=row, column=1, value=idx + 1)
        c.font = data_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border

        # 数据名称（带超链接）
        c = ws_toc.cell(row=row, column=2, value=title)
        c.font = link_font
        c.hyperlink = f"#'{sheet_name}'!A1"
        c.border = thin_border

        # 发布日期
        c = ws_toc.cell(row=row, column=3, value=publish_date)
        c.font = data_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border

        # 跳转链接（文字提示）
        c = ws_toc.cell(row=row, column=4, value="点击跳转 →")
        c.font = link_font
        c.hyperlink = f"#'{sheet_name}'!A1"
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border

    # 目录列宽
    ws_toc.column_dimensions["A"].width = 8
    ws_toc.column_dimensions["B"].width = 42
    ws_toc.column_dimensions["C"].width = 16
    ws_toc.column_dimensions["D"].width = 14

    # ── Sheet 2: 汇总表（所有数据纵向追加，加"数据来源"列） ──
    ws_summary = wb.create_sheet(title="汇总表")
    ws_summary.sheet_properties.tabColor = "C55A11"

    # 汇总表标题
    ws_summary.merge_cells("A1:F1")
    st = ws_summary.cell(row=1, column=1, value=f"{indicator_name} — 全量数据汇总（按日期升序）")
    st.font = title_font
    st.alignment = Alignment(horizontal="center", vertical="center")
    ws_summary.row_dimensions[1].height = 36

    # 汇总表表头
    summary_headers = ["序号", "指标", "当月值", "同比增长(%)", "累计值", "同比增长(%)", "数据来源"]
    for col_idx, h in enumerate(summary_headers, 1):
        cell = ws_summary.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    summary_row = 4
    seq = 1

    for title, publish_date, header, data_rows in all_sheets:
        # 写入数据来源分隔行
        ws_summary.merge_cells(start_row=summary_row, start_column=1, end_row=summary_row, end_column=len(summary_headers))
        sep = ws_summary.cell(row=summary_row, column=1, value=f"▸ {title}" + (f"（{publish_date}）" if publish_date else ""))
        sep.font = cat_font
        sep.fill = cat_fill
        sep.alignment = Alignment(vertical="center")
        for ci in range(1, len(summary_headers) + 1):
            ws_summary.cell(row=summary_row, column=ci).border = thin_border
            ws_summary.cell(row=summary_row, column=ci).fill = cat_fill
        summary_row += 1

        # 写入该数据源的每一行数据
        for row in data_rows:
            # 跳过分隔标题行（如"限额以上单位主要商品零售情况"）
            if not row or all(str(c).strip() == "" for c in row):
                continue
            row_text = " ".join(str(c) for c in row)
            if row_text.strip() in ["限额以上单位主要商品零售情况", "限额以上单位主要商品零售情况"]:
                continue

            # 第1列：序号
            c = ws_summary.cell(row=summary_row, column=1, value=seq)
            c.font = data_font
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = thin_border

            # 第2-6列：从原始数据映射
            # 原始列结构通常是：指标 | 当月值 | 同比增长 | 累计值 | 累计同比增长
            # 但不同月份列数可能不同（如1-2月只有3列），需要灵活映射
            indicator_name_val = row[0] if len(row) > 0 else ""
            c = ws_summary.cell(row=summary_row, column=2, value=indicator_name_val)
            c.font = data_font
            c.alignment = data_alignment
            c.border = thin_border

            # 数值列：从第2列开始映射到汇总表的第3-6列
            for src_idx in range(1, min(len(row), 5)):  # 最多取4个数值列
                val = row[src_idx]
                c = ws_summary.cell(row=summary_row, column=2 + src_idx)
                if isinstance(val, str):
                    try:
                        num = float(val)
                        c.value = num
                        c.alignment = number_alignment
                    except ValueError:
                        c.value = val
                        c.alignment = data_alignment
                else:
                    c.value = val
                    c.alignment = data_alignment
                c.font = data_font
                c.border = thin_border

            # 如果原始数据不足4个数值列，补空
            for fill_col in range(2 + len(row), 7):
                c = ws_summary.cell(row=summary_row, column=fill_col, value="")
                c.border = thin_border

            # 最后一列：数据来源（标题+日期）
            source_text = title + (f"（{publish_date}）" if publish_date else "")
            c = ws_summary.cell(row=summary_row, column=7, value=source_text)
            c.font = Font(name="微软雅黑", size=9, color="666666")
            c.alignment = Alignment(vertical="center", wrap_text=True)
            c.border = thin_border

            summary_row += 1
            seq += 1

    # 汇总表列宽
    ws_summary.column_dimensions["A"].width = 6
    ws_summary.column_dimensions["B"].width = 28
    ws_summary.column_dimensions["C"].width = 14
    ws_summary.column_dimensions["D"].width = 14
    ws_summary.column_dimensions["E"].width = 14
    ws_summary.column_dimensions["F"].width = 14
    ws_summary.column_dimensions["G"].width = 32

    # ── Sheet 3+: 各数据源的详细数据 ──
    for idx, (title, publish_date, header, data_rows) in enumerate(all_sheets):
        sheet_name = sheet_name_map[idx][0]

        ws = wb.create_sheet(title=sheet_name)

        # 副标题行（数据来源信息）
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(len(header), 3))
        src_cell = ws.cell(row=1, column=1, value=f"数据来源：{title}" + (f"  |  发布日期：{publish_date}" if publish_date else ""))
        src_cell.font = Font(name="微软雅黑", size=9, color="888888", italic=True)
        src_cell.alignment = Alignment(vertical="center")
        ws.row_dimensions[1].height = 20

        # 写入表头（从第2行开始）
        if header:
            for col_idx, h in enumerate(header, 1):
                cell = ws.cell(row=2, column=col_idx, value=h)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = thin_border

        # 写入数据行
        for row_idx, row in enumerate(data_rows, 3 if header else 2):
            for col_idx, val in enumerate(row, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                # 尝试转为数值
                if isinstance(val, str):
                    try:
                        num = float(val)
                        cell.value = num
                        cell.alignment = number_alignment
                    except ValueError:
                        cell.value = val
                        cell.alignment = data_alignment
                else:
                    cell.value = val
                    cell.alignment = data_alignment
                cell.font = data_font
                cell.border = thin_border

        # 自动调整列宽
        for col_idx in range(1, max(len(header), 3) + 1):
            col_letter = get_column_letter(col_idx)
            max_length = 0
            for row in ws.iter_rows(min_col=col_idx, max_col=col_idx, min_row=1, max_row=ws.max_row):
                for cell in row:
                    if cell.value and not isinstance(cell, MergedCell):
                        cell_len = len(str(cell.value))
                        cn_count = sum(1 for c in str(cell.value) if '\u4e00' <= c <= '\u9fff')
                        cell_len = cell_len + cn_count
                        max_length = max(max_length, cell_len)
            ws.column_dimensions[col_letter].width = min(max_length + 4, 50)

    # 保存到内存
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # 返回文件
    safe_name = re.sub(r'[\\/*?:[\]]', '', indicator_name)
    filename = f"{safe_name}_全量数据.xlsx"

    return Response(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"
        }
    )


def parse_html_table(table):
    """从 HTML table 标签中解析数据"""
    rows = table.find_all("tr")
    if not rows:
        return [], []

    all_rows = []
    for tr in rows:
        cells = tr.find_all(["th", "td"])
        row_data = [cell.get_text(strip=True) for cell in cells]
        if any(c for c in row_data):
            all_rows.append(row_data)

    if not all_rows:
        return [], []

    # 找表头行
    header_idx = 0
    for i, row in enumerate(all_rows):
        if "指标" in " ".join(row):
            header_idx = i
            break

    header = all_rows[header_idx]
    data = all_rows[header_idx + 1:]

    # 过滤注释行
    clean_data = []
    for row in data:
        row_text = " ".join(row)
        if any(kw in row_text for kw in ["统计范围", "数据来源", "指标解释", "说明", "注：", "注:"]):
            break
        if all(c == "" for c in row):
            if clean_data:
                break
            continue
        clean_data.append(row)

    return header, clean_data


# ══════════════════════════════════════════════════════════════
# 端点 9: 导出合并进度查询（SSE 流式返回进度）
# ══════════════════════════════════════════════════════════════
@app.route("/api/export-merged-status")
def export_merged_status():
    """返回合并导出的状态（前端轮询用）"""
    return jsonify({"status": "ok"})


# ══════════════════════════════════════════════════════════════
# 提供前端页面
# ══════════════════════════════════════════════════════════════
@app.route("/")
def serve_index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")


# ══════════════════════════════════════════════════════════════
# 健康检查
# ══════════════════════════════════════════════════════════════
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "timestamp": time.time()})


# ══════════════════════════════════════════════════════════════
# 主入口
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  上海市统计局数据抓取代理服务器")
    print("  访问 http://localhost:5000 打开前端页面")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
