import os
import re
import io
import sys
import json
import time
import zipfile
import hashlib
import logging
import threading
from urllib.parse import quote, urljoin

import requests
from flask import Flask, jsonify, request, send_file, make_response
from flask_cors import CORS
from bs4 import BeautifulSoup
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)

BASE_URL = "https://www.topklout.com"
API_BASE = "https://motion.topklout.com/api/Apidata/web"
STATIC_BASE = "https://static.topklout.com"
HOME_URL = f"{BASE_URL}/#/home"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": BASE_URL + "/",
}

reports_cache = []
cache_lock = threading.Lock()
cache_timestamp = 0
CACHE_TTL = 600

pdf_cache_dir = os.path.join(BASE_DIR, "pdf_cache")
os.makedirs(pdf_cache_dir, exist_ok=True)


def generate_report_id(title):
    return hashlib.md5(title.encode("utf-8")).hexdigest()[:12]


def safe_filename(title):
    name = re.sub(r'[<>:"/\\|?*]', "_", title)
    return name[:100]


def try_api_layer():
    logger.info("[Layer1] Starting API interception via Playwright...")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("[Layer1] Playwright not installed, skipping")
        return None

    captured_data = {}

    def on_response(response):
        url = response.url
        if "motion.topklout.com" in url and "reportList" in url:
            try:
                body = response.text()
                data = json.loads(body)
                if data.get("result") == "success":
                    captured_data["reportList"] = data
                    logger.info(f"[Layer1] Captured reportList API response")
            except Exception as e:
                logger.warning(f"[Layer1] Failed to parse response: {e}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.on("response", on_response)

            logger.info("[Layer1] Navigating to homepage...")
            page.goto(HOME_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(8000)

            reports_nav = page.query_selector("text=报告下载")
            if reports_nav:
                logger.info("[Layer1] Clicking '报告下载' to trigger API...")
                reports_nav.click()
                page.wait_for_timeout(5000)

            browser.close()

        if "reportList" in captured_data:
            data = captured_data["reportList"]
            reports = data.get("list", {}).get("report_list", [])
            tags = data.get("list", {}).get("reportTag", [])
            logger.info(f"[Layer1] Got {len(reports)} reports, {len(tags)} tags from API")

            tag_map = {}
            for t in tags:
                tag_map[t.get("id", "")] = t.get("tag_name", "")

            normalized = []
            seen_ids = set()
            for r in reports:
                report_id = r.get("report_id", "")
                title = r.get("r_name", "").strip()
                if not title or report_id in seen_ids:
                    continue
                seen_ids.add(report_id)

                cover = r.get("covers_url", "")
                if cover and not cover.startswith("http"):
                    cover = f"{STATIC_BASE}{cover}"

                tags_str = r.get("r_tags", "")
                labels = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

                pdf_url = r.get("pdf_file_url", "")

                normalized.append({
                    "id": report_id or generate_report_id(title),
                    "title": title,
                    "cover_url": cover,
                    "labels": labels,
                    "page_url": f"{BASE_URL}/#/home",
                    "pdf_url": pdf_url,
                    "summary": r.get("r_summary", ""),
                    "date": r.get("up_times", ""),
                    "preview_num": r.get("preview_num", "0"),
                    "downloads": r.get("downloads", "0"),
                })

            if normalized:
                logger.info(f"[Layer1] Normalized {len(normalized)} reports")
                return normalized

    except Exception as e:
        logger.warning(f"[Layer1] Playwright API interception failed: {e}")

    logger.info("[Layer1] No data from API interception")
    return None


def try_html_layer():
    logger.info("[Layer2] Starting HTML DOM parsing via Playwright...")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("[Layer2] Playwright not installed, skipping")
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            logger.info("[Layer2] Navigating to homepage...")
            page.goto(HOME_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            html_content = page.content()
            browser.close()

        soup = BeautifulSoup(html_content, "html.parser")

        reports = []
        seen_titles = set()

        slides = soup.select(".reports-list .swiper-slide")
        logger.info(f"[Layer2] Found {len(slides)} swiper slides")

        for slide in slides:
            title_el = slide.select_one(".rep-title")
            cover_el = slide.select_one(".cover img")
            label_els = slide.select(".label")

            title = title_el.get_text(strip=True) if title_el else ""
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)

            cover = ""
            if cover_el:
                cover = cover_el.get("src", "") or cover_el.get("data-src", "")

            labels = [l.get_text(strip=True) for l in label_els]

            reports.append({
                "id": generate_report_id(title),
                "title": title,
                "cover_url": cover,
                "labels": labels,
                "page_url": HOME_URL,
                "pdf_url": "",
            })

        if reports:
            logger.info(f"[Layer2] Parsed {len(reports)} reports from HTML")
            return reports

    except Exception as e:
        logger.warning(f"[Layer2] HTML DOM parsing failed: {e}")

    logger.info("[Layer2] No data from HTML parsing")
    return None


def try_browser_layer():
    logger.info("[Layer3] Starting Playwright browser extraction...")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("[Layer3] Playwright not installed, skipping")
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            logger.info("[Layer3] Navigating to homepage...")
            page.goto(HOME_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

            reports = []
            seen_titles = set()

            items = page.query_selector_all(".rep-title")
            covers = page.query_selector_all(".cover img")

            logger.info(f"[Layer3] Found {len(items)} report titles, {len(covers)} covers")

            for i, item in enumerate(items):
                title = item.inner_text().strip()
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)

                cover = ""
                if i < len(covers):
                    cover = covers[i].get_attribute("src") or ""

                labels = []
                try:
                    parent = item.evaluate("el => el.closest('.swiper-slide')")
                    if parent:
                        label_els = page.query_selector_all(".swiper-slide .label")
                        labels = [l.inner_text().strip() for l in label_els[:5]]
                except:
                    pass

                reports.append({
                    "id": generate_report_id(title),
                    "title": title,
                    "cover_url": cover,
                    "labels": labels,
                    "page_url": HOME_URL,
                    "pdf_url": "",
                })

            browser.close()

        if reports:
            logger.info(f"[Layer3] Extracted {len(reports)} reports via browser")
            return reports

    except Exception as e:
        logger.warning(f"[Layer3] Browser extraction failed: {e}")

    logger.info("[Layer3] No data from browser extraction")
    return None


def fetch_all_reports():
    global reports_cache, cache_timestamp

    if reports_cache and (time.time() - cache_timestamp) < CACHE_TTL:
        logger.info(f"Using cached reports ({len(reports_cache)} items)")
        return reports_cache

    logger.info("Fetching all reports...")

    reports = try_api_layer()
    source = "API"

    if not reports:
        reports = try_html_layer()
        source = "HTML"

    if not reports:
        reports = try_browser_layer()
        source = "Browser"

    if reports:
        with cache_lock:
            reports_cache = reports
            cache_timestamp = time.time()
        logger.info(f"Fetched {len(reports)} reports from {source}")
    else:
        logger.error("All layers failed, no reports fetched")

    return reports or []


def fetch_report_pdf(report):
    pdf_url = report.get("pdf_url", "")
    title = report.get("title", "unknown")
    cover_url = report.get("cover_url", "")

    if pdf_url:
        try:
            resp = requests.get(pdf_url, headers=HEADERS, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 1000:
                return resp.content
        except Exception as e:
            logger.warning(f"Failed to download PDF from {pdf_url}: {e}")

    try:
        from playwright.sync_api import sync_playwright
        logger.info(f"Trying Playwright to get PDF for: {title}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            pdf_urls = []

            def on_response(response):
                url = response.url
                ct = response.headers.get("content-type", "")
                if "pdf" in ct or url.endswith(".pdf"):
                    pdf_urls.append(url)

            page.on("response", on_response)
            page.goto(HOME_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

            title_el = page.query_selector(f"text={title[:20]}")
            if title_el:
                title_el.click()
                page.wait_for_timeout(2000)

            preview_btn = page.query_selector("text=在线预览")
            if preview_btn:
                preview_btn.click()
                page.wait_for_timeout(5000)

                for ctx_page in page.context.pages:
                    if ctx_page != page:
                        new_url = ctx_page.url
                        file_match = re.search(r'file=([^&]+)', new_url)
                        if file_match:
                            file_url = file_match.group(1)
                            try:
                                pdf_resp = requests.get(file_url, headers=HEADERS, timeout=30)
                                if pdf_resp.status_code == 200:
                                    browser.close()
                                    return pdf_resp.content
                            except:
                                pass

            browser.close()

    except Exception as e:
        logger.warning(f"Playwright PDF extraction failed: {e}")

    if cover_url:
        try:
            logger.info(f"Generating PDF from cover image: {cover_url}")
            resp = requests.get(cover_url, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content))
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                pdf_bytes = io.BytesIO()
                img.save(pdf_bytes, format="PDF")
                return pdf_bytes.getvalue()
        except Exception as e:
            logger.warning(f"Failed to generate PDF from cover: {e}")

    return None


def fetch_image(image_url):
    try:
        resp = requests.get(image_url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.content, resp.headers.get("content-type", "image/png")
    except Exception as e:
        logger.warning(f"Failed to fetch image {image_url}: {e}")
    return None, None


@app.route("/")
def index():
    return send_file(os.path.join(BASE_DIR, "index.html"))


@app.route("/api/reports")
def api_reports():
    reports = fetch_all_reports()
    return jsonify({
        "success": True,
        "count": len(reports),
        "reports": reports,
    })


@app.route("/api/refresh")
def api_refresh():
    global reports_cache, cache_timestamp
    with cache_lock:
        reports_cache = []
        cache_timestamp = 0
    reports = fetch_all_reports()
    return jsonify({
        "success": True,
        "count": len(reports),
        "reports": reports,
    })


@app.route("/api/download-pdf/<report_id>")
def api_download_pdf(report_id):
    reports = fetch_all_reports()
    report = next((r for r in reports if r["id"] == report_id), None)

    if not report:
        return jsonify({"success": False, "error": "Report not found"}), 404

    cache_file = os.path.join(pdf_cache_dir, f"{safe_filename(report['title'])}.pdf")
    if os.path.exists(cache_file):
        return send_file(cache_file, mimetype="application/pdf", as_attachment=True,
                        download_name=f"{safe_filename(report['title'])}.pdf")

    pdf_content = fetch_report_pdf(report)
    if pdf_content:
        with open(cache_file, "wb") as f:
            f.write(pdf_content)
        return send_file(io.BytesIO(pdf_content), mimetype="application/pdf", as_attachment=True,
                        download_name=f"{safe_filename(report['title'])}.pdf")

    return jsonify({"success": False, "error": "Failed to generate PDF"}), 500


@app.route("/api/download-batch", methods=["POST"])
def api_download_batch():
    data = request.get_json() or {}
    report_ids = data.get("ids", [])
    download_all = data.get("all", False)

    reports = fetch_all_reports()

    if download_all:
        selected = reports
    else:
        selected = [r for r in reports if r["id"] in report_ids]

    if not selected:
        return jsonify({"success": False, "error": "No reports selected"}), 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for report in selected:
            title = report.get("title", "unknown")
            cache_file = os.path.join(pdf_cache_dir, f"{safe_filename(title)}.pdf")

            if os.path.exists(cache_file):
                with open(cache_file, "rb") as f:
                    pdf_content = f.read()
            else:
                pdf_content = fetch_report_pdf(report)
                if pdf_content:
                    with open(cache_file, "wb") as f:
                        f.write(pdf_content)

            if pdf_content:
                zf.writestr(f"{safe_filename(title)}.pdf", pdf_content)

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip", as_attachment=True,
                    download_name="topklout_reports.zip")


@app.route("/api/proxy-image")
def api_proxy_image():
    image_url = request.args.get("url", "")
    if not image_url:
        return jsonify({"error": "Missing url parameter"}), 400

    allowed_domains = ["static.topklout.com", "topklout.com"]
    from urllib.parse import urlparse
    parsed = urlparse(image_url)
    if not any(domain in parsed.netloc for domain in allowed_domains):
        return jsonify({"error": "Domain not allowed"}), 403

    content, content_type = fetch_image(image_url)
    if content:
        response = make_response(content)
        response.headers["Content-Type"] = content_type
        response.headers["Cache-Control"] = "public, max-age=86400"
        return response

    return jsonify({"error": "Failed to fetch image"}), 500


if __name__ == "__main__":
    port = 5001
    logger.info(f"Starting Topklout Report Server on port {port}...")
    logger.info(f"Open http://localhost:{port} in your browser")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
