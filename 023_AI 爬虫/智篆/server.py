import os
import re
import io
import sys
import time
import hashlib
import logging
import html as html_module
from urllib.parse import urljoin, quote, unquote

import requests
from flask import Flask, jsonify, request, send_file, send_from_directory
from bs4 import BeautifulSoup
from PIL import Image

app = Flask(__name__)

BASE_URL = "https://zhizhuan100.com.cn"
ANALYSIS_URL = f"{BASE_URL}/analysis"
IMAGE_DOMAIN = "aka.doubaocdn.com"
WANWANG_DOMAIN = "wanwang.xin"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

CACHE = {"reports": None, "timestamp": 0}
DETAIL_CACHE = {}
CACHE_TTL = 600
TOTAL_PAGES = 5

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_from_cache(key):
    if key in DETAIL_CACHE:
        entry = DETAIL_CACHE[key]
        if time.time() - entry["timestamp"] < CACHE_TTL:
            return entry["data"]
    return None


def set_cache(key, data):
    DETAIL_CACHE[key] = {"data": data, "timestamp": time.time()}


def extract_report_id(link):
    match = re.search(r"/productinfo/(\d+)\.html", link)
    if match:
        return match.group(1)
    return hashlib.md5(link.encode()).hexdigest()[:12]


def normalize_image_url(img_url):
    if not img_url:
        return ""
    img_url = html_module.unescape(img_url)
    if img_url.startswith("//"):
        img_url = "https:" + img_url
    return img_url


def try_api_layer():
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        resp = session.get(ANALYSIS_URL, timeout=20)
        resp.encoding = "utf-8"
        logger.info(f"[Layer1] Fetched analysis page, cookies: {list(session.cookies.keys())}")
    except Exception as e:
        logger.warning(f"[Layer1] Failed to fetch analysis page: {e}")
        return None

    all_items = []
    seen_ids = set()
    api_url = f"{BASE_URL}/Designer/Common/GetData"

    for page_index in range(10):
        form_data = {
            "dataType": "product",
            "key": "",
            "pageIndex": str(page_index),
            "pageSize": "20",
            "selectCategory": "889154",
            "selectId": "",
            "dateFormater": "yyyy-MM-dd",
            "orderByField": "createtime",
            "orderByType": "desc",
            "templateId": "1647211",
            "postData": "",
            "es": "false",
            "setTop": "true",
        }
        try:
            api_resp = session.post(
                api_url,
                data=form_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": ANALYSIS_URL,
                },
                timeout=15,
            )
            api_resp.raise_for_status()
            result = api_resp.json()

            if not result.get("IsSuccess"):
                logger.warning(f"[Layer1] API pageIndex={page_index} returned IsSuccess=false")
                break

            data_list = result.get("Data", [])
            if not data_list:
                logger.info(f"[Layer1] API pageIndex={page_index} returned empty Data, stopping")
                break

            new_count = 0
            for item in data_list:
                item_id = str(item.get("Id", ""))
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                all_items.append(item)
                new_count += 1

            logger.info(f"[Layer1] API pageIndex={page_index}: {len(data_list)} items, {new_count} new (total: {len(all_items)})")
        except Exception as e:
            logger.warning(f"[Layer1] API pageIndex={page_index} failed: {e}")
            break

    if all_items:
        logger.info(f"[Layer1] Total items collected: {len(all_items)}")
    return all_items if all_items else None


def parse_body_js_layer():
    try:
        resp = requests.get(ANALYSIS_URL, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        html_text = resp.text
    except Exception as e:
        logger.warning(f"Failed to fetch analysis page: {e}")
        return None

    body_js_match = re.search(r"src='([^']*Body\.js[^']*)'", html_text)
    if not body_js_match:
        body_js_match = re.search(r'src="([^"]*Body\.js[^"]*)"', html_text)
    if not body_js_match:
        logger.warning("Body.js URL not found in page")
        return None

    body_js_url = body_js_match.group(1)
    if body_js_url.startswith("//"):
        body_js_url = "https:" + body_js_url

    logger.info(f"Fetching Body.js: {body_js_url[:80]}...")
    try:
        js_resp = requests.get(body_js_url, headers=HEADERS, timeout=20)
        js_content = js_resp.text
    except Exception as e:
        logger.warning(f"Failed to fetch Body.js: {e}")
        return None

    all_reports = []
    seen_ids = set()

    items = re.findall(
        r'data-list-id=\\"(\d+)\\"[^>]*?data-list-picurl=\\"([^"\\]*(?:\\.[^"\\]*)*)\\"[^>]*?'
        r'href=\\"(/productinfo/\d+\.html\?templateId=\d+)\\"[^>]*?'
        r'\u003ch5[^>]*\u003e(.*?)\u003c/h5\u003e',
        js_content,
        re.DOTALL,
    )

    if not items:
        items = re.findall(
            r'data-list-picurl=\\"([^"\\]*(?:\\.[^"\\]*)*)\\"[^>]*?data-list-id=\\"(\d+)\\"[^>]*?'
            r'href=\\"(/productinfo/\d+\.html\?templateId=\d+)\\"[^>]*?'
            r'\u003ch5[^>]*\u003e(.*?)\u003c/h5\u003e',
            js_content,
            re.DOTALL,
        )
        if items:
            items = [(i[1], i[0], i[2], i[3]) for i in items]

    for pid, picurl, href, title_raw in items:
        if pid in seen_ids:
            continue
        seen_ids.add(pid)

        title = re.sub(r'<[^>]+>', '', title_raw).strip()
        title = html_module.unescape(title.replace("\\u0026", "&"))
        title = title.encode("raw_unicode_escape").decode("utf-8", errors="replace") if "\\u" in title_raw else title

        image = picurl.replace("\\/", "/").replace("\\u0026", "&")
        image = normalize_image_url(image)

        full_link = BASE_URL + href.replace("\\u0026", "&").replace("\\/", "/")

        all_reports.append({
            "id": pid,
            "title": title,
            "link": full_link,
            "image": image,
        })

    if all_reports:
        logger.info(f"Body.js parsing found {len(all_reports)} products from page 1")
    return all_reports if all_reports else None


def playwright_layer():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("Playwright not installed, skipping browser layer")
        return None

    all_reports = []
    seen_ids = set()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            logger.info("Playwright: Loading page 1...")
            page.goto(ANALYSIS_URL, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            page.wait_for_timeout(3000)

            def collect_visible_items():
                items = []
                elements = page.query_selector_all("a[href*='productinfo']")
                for el in elements:
                    href = el.get_attribute("href") or ""
                    if not href or not re.search(r"/productinfo/\d+\.html", href):
                        continue

                    pid_match = re.search(r"/productinfo/(\d+)\.html", href)
                    pid = pid_match.group(1) if pid_match else ""
                    if not pid or pid in seen_ids:
                        continue

                    title_el = el.query_selector("h5")
                    title = ""
                    if title_el:
                        try:
                            title = title_el.evaluate("el => el.textContent") or ""
                            title = title.strip()
                        except Exception:
                            pass

                    if not title:
                        try:
                            title = el.evaluate("el => el.textContent") or ""
                            title = title.strip()
                        except Exception:
                            pass

                    if not title:
                        continue

                    image = ""
                    img = el.query_selector("img")
                    if img:
                        image = img.get_attribute("src") or ""
                    image = normalize_image_url(image)

                    full_link = urljoin(BASE_URL, href)
                    seen_ids.add(pid)
                    items.append({
                        "id": pid,
                        "title": title,
                        "link": full_link,
                        "image": image,
                    })
                return items

            page1_items = collect_visible_items()
            all_reports.extend(page1_items)
            logger.info(f"Playwright page 1: {len(page1_items)} items")

            for pg in range(2, TOTAL_PAGES + 1):
                try:
                    logger.info(f"Playwright: Navigating to page {pg}...")
                    pager_btn = page.query_selector(f"li[jp-role='page'][jp-data='{pg}'] a")
                    if not pager_btn:
                        pager_btn = page.query_selector(f"a:has-text('{pg}')")
                    if not pager_btn:
                        pager_btns = page.query_selector_all(".xn-pager a")
                        for btn in pager_btns:
                            if btn.inner_text().strip() == str(pg):
                                pager_btn = btn
                                break
                    if not pager_btn:
                        logger.warning(f"Page {pg} button not found")
                        continue

                    pager_btn.click()
                    page.wait_for_timeout(4000)

                    new_items = collect_visible_items()
                    all_reports.extend(new_items)
                    logger.info(f"Playwright page {pg}: {len(new_items)} new items (total: {len(all_reports)})")
                except Exception as e:
                    logger.warning(f"Playwright page {pg} error: {e}")
                    continue

            browser.close()
            logger.info(f"Playwright total: {len(all_reports)} items")

    except Exception as e:
        logger.error(f"Playwright layer error: {e}")
        return None

    return all_reports if all_reports else None


def fetch_all_reports():
    now = time.time()
    if CACHE["reports"] and (now - CACHE["timestamp"]) < CACHE_TTL:
        logger.info("Returning cached reports")
        return CACHE["reports"]

    logger.info("Layer 1: Trying hidden API + Body.js...")
    reports = None
    api_result = try_api_layer()
    if api_result:
        reports = normalize_api_data(api_result)
        if reports and len(reports) >= 80:
            logger.info(f"Layer 1 succeeded: {len(reports)} reports")
            CACHE["reports"] = reports
            CACHE["timestamp"] = time.time()
            return reports
        elif reports and len(reports) >= 15:
            logger.info(f"Layer 1 partial: {len(reports)} reports (below 80 threshold, using as fallback)")

    logger.info("Layer 2: Parsing Body.js from CDN...")
    js_result = parse_body_js_layer()
    if js_result and len(js_result) >= 15:
        logger.info(f"Layer 2 succeeded: {len(js_result)} reports")
        CACHE["reports"] = js_result
        CACHE["timestamp"] = time.time()
        return js_result

    if reports and len(reports) >= 15:
        logger.info(f"Using Layer 1 partial result: {len(reports)} reports")
        CACHE["reports"] = reports
        CACHE["timestamp"] = time.time()
        return reports

    logger.info("Layer 3: Using Playwright browser (all pages)...")
    browser_result = playwright_layer()
    if browser_result:
        logger.info(f"Layer 3 succeeded: {len(browser_result)} reports")
        CACHE["reports"] = browser_result
        CACHE["timestamp"] = time.time()
        return browser_result

    logger.error("All three layers failed")
    return []


def normalize_api_data(data):
    reports = []
    seen_ids = set()
    for item in data:
        raw_id = item.get("Id") or item.get("id")
        link = item.get("LinkUrl") or item.get("link") or item.get("url") or item.get("href", "")
        if not link:
            if raw_id:
                link = f"{BASE_URL}/productinfo/{raw_id}.html?templateId=1647211"
            else:
                continue

        if not link.startswith("http"):
            link = BASE_URL + link if link.startswith("/") else urljoin(BASE_URL, link)

        if raw_id:
            report_id = str(raw_id)
        else:
            report_id = extract_report_id(link)
        if report_id in seen_ids:
            continue

        title = item.get("Name") or item.get("title") or item.get("name", "")
        raw_image = item.get("PicUrl") or item.get("image") or item.get("cover") or item.get("img") or item.get("ThumbnailUrl", "")
        image = normalize_image_url(raw_image)

        seen_ids.add(report_id)
        reports.append({
            "id": report_id,
            "title": title,
            "link": link,
            "image": image,
        })
    return reports


def fetch_report_detail_images(report_id, report_link):
    cache_key = f"detail_{report_id}"
    cached = get_from_cache(cache_key)
    if cached is not None:
        return cached

    images = []
    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers["Referer"] = report_link

    try:
        resp = session.get(report_link, timeout=20)
        resp.encoding = "utf-8"
        html_text = resp.text

        body_js_match = re.search(r"src='([^']*Body\.js[^']*)'", html_text)
        if not body_js_match:
            body_js_match = re.search(r'src="([^"]*Body\.js[^"]*)"', html_text)
        if body_js_match:
            body_js_url = body_js_match.group(1)
            if body_js_url.startswith("//"):
                body_js_url = "https:" + body_js_url

            js_headers = dict(HEADERS)
            js_headers["Referer"] = report_link
            js_resp = session.get(body_js_url, headers=js_headers, timeout=20)
            js_content = js_resp.text

            if "403 Forbidden" not in js_content:
                found = re.findall(
                    r'(//img\.wanwang\.xin[^"\'\\]+\.(?:jpg|jpeg|png|gif|webp))',
                    js_content,
                    re.IGNORECASE,
                )
                for img in found:
                    full_url = "https:" + img
                    if full_url not in images:
                        images.append(full_url)

        if not images:
            found = re.findall(
                r'(//aka\.doubaocdn\.com[^"\'\\]+\.(?:jpg|jpeg|png|gif|webp))',
                html_text,
                re.IGNORECASE,
            )
            for img in found:
                full_url = "https:" + img
                if full_url not in images:
                    images.append(full_url)
    except Exception as e:
        logger.warning(f"Requests detail page failed: {e}")

    if images:
        logo_patterns = [r"logo", r"icon", r"avatar", r"qrcode", r"wechat", r"footer", r"header-banner"]
        filtered = []
        for url in images:
            if not any(kw in url.lower() for kw in logo_patterns):
                filtered.append(url)
        result = filtered if filtered else images
        set_cache(cache_key, result)
        return result

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1920, "height": 1080},
            )
            pw_page = context.new_page()

            try:
                pw_page.goto(report_link, wait_until="domcontentloaded", timeout=30000)
                try:
                    pw_page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass
                pw_page.wait_for_timeout(3000)

                img_elements = pw_page.query_selector_all("img")
                for img_el in img_elements:
                    src = img_el.get_attribute("data-original") or img_el.get_attribute("data-src") or img_el.get_attribute("src") or ""
                    if not src:
                        continue
                    src = re.sub(r'^https?://aka\.doubaocdn\.com/s/', 'https://img.wanwang.xin/', src)
                    if not src.startswith("http"):
                        if src.startswith("//"):
                            src = "https:" + src
                        elif src.startswith("/"):
                            src = BASE_URL + src
                    if re.search(r'\.(?:jpg|jpeg|png|gif|webp)', src, re.IGNORECASE):
                        if src not in images:
                            images.append(src)
            except Exception as e:
                logger.warning(f"Playwright detail page failed: {e}")
            finally:
                browser.close()
    except ImportError:
        logger.warning("Playwright not installed")
    except Exception as e:
        logger.warning(f"Playwright error: {e}")

    logo_patterns = [r"logo", r"icon", r"avatar", r"qrcode", r"wechat", r"footer", r"header-banner"]
    filtered = []
    for url in images:
        if not any(kw in url.lower() for kw in logo_patterns):
            filtered.append(url)
    result = filtered if filtered else images
    set_cache(cache_key, result)
    return result


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/reports")
def api_reports():
    reports = fetch_all_reports()
    return jsonify({"reports": reports})


@app.route("/api/download/<report_id>")
def api_download(report_id):
    reports = fetch_all_reports()
    target = None
    for r in reports:
        if r["id"] == report_id:
            target = r
            break

    if not target:
        return jsonify({"error": "Report not found"}), 404

    images = fetch_report_detail_images(report_id, target["link"])
    if not images:
        return jsonify({"error": "No images found"}), 404

    pdf_images = []
    for img_url in images:
        try:
            img_headers = dict(HEADERS)
            img_headers["Referer"] = target["link"]
            img_resp = requests.get(img_url, headers=img_headers, timeout=20)
            img_resp.raise_for_status()
            img = Image.open(io.BytesIO(img_resp.content))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            pdf_images.append(img)
        except Exception as e:
            logger.warning(f"Failed to download/process image {img_url}: {e}")
            continue

    if not pdf_images:
        return jsonify({"error": "No images could be processed"}), 404

    buf = io.BytesIO()
    if len(pdf_images) == 1:
        pdf_images[0].save(buf, format="PDF")
    else:
        pdf_images[0].save(buf, format="PDF", save_all=True, append_images=pdf_images[1:])
    buf.seek(0)

    safe_title = re.sub(r'[\\/:*?"<>|]', "_", target["title"])
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{safe_title}.pdf",
    )


@app.route("/api/proxy-image")
def api_proxy_image():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    url = unquote(url)
    if not url.startswith("http"):
        if url.startswith("//"):
            url = "https:" + url
        else:
            return jsonify({"error": "Invalid URL"}), 400

    try:
        proxy_headers = dict(HEADERS)
        proxy_headers["Referer"] = BASE_URL
        resp = requests.get(url, headers=proxy_headers, timeout=15, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        return send_file(
            io.BytesIO(resp.content),
            mimetype=content_type,
        )
    except Exception as e:
        logger.error(f"Proxy image failed: {e}")
        return jsonify({"error": "Failed to fetch image"}), 502


if __name__ == "__main__":
    print("=" * 50)
    print("  ZhiZhuan100 Data Report Crawler Server")
    print(f"  Listening: http://localhost:5000")
    print(f"  API Endpoints:")
    print(f"    GET /api/reports       - Get all reports")
    print(f"    GET /api/download/<id> - Download report PDF")
    print(f"    GET /api/proxy-image   - Image proxy")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False)
