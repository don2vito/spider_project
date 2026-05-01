# -*- coding: utf-8 -*-
"""
Electronic Textbook Downloader - Proxy Server
Fetches textbook data from smartedu.cn and provides API + PDF download proxy.
"""

import json
import re
import threading
import urllib.parse
from flask import Flask, jsonify, request, send_file, Response
import requests

app = Flask(__name__)

# ── Global Cache ──────────────────────────────────────────────
_data_cache = {
    "textbooks": [],
    "filters": {},
    "pdf_url_cache": {},
    "loaded": False,
}

# ── Constants ─────────────────────────────────────────────────
VERSION_URL = "https://s-file-2.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/version/data_version.json"
DETAIL_API = "https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/details/{content_id}.json"

DIMENSION_IDS = ["zxxxd", "zxxxk", "zxxbb", "zxxnj", "zxxcc"]
DIMENSION_LABELS = {
    "zxxxd": "学段",
    "zxxxk": "学科",
    "zxxbb": "版本",
    "zxxnj": "年级",
    "zxxcc": "册别",
}


# ── Data Loading ──────────────────────────────────────────────
def load_data():
    """Load all textbook data from CDN JSON shards."""
    print("Fetching version info...")
    try:
        ver_resp = requests.get(VERSION_URL, timeout=30)
        ver_data = ver_resp.json()
        data_urls = [u.strip() for u in ver_data["urls"].split(",")]
        print(f"Found {len(data_urls)} data shards.")
    except Exception as e:
        print(f"Warning: Could not fetch version file, using fallback URLs. Error: {e}")
        data_urls = [
            "https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/part_100.json",
            "https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/part_101.json",
            "https://s-file-2.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/part_102.json",
            "https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/part_103.json",
        ]

    results = [None] * len(data_urls)
    errors = []

    def fetch_shard(i, url):
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            results[i] = resp.json()
            print(f"  Shard {i+1}/{len(data_urls)} loaded: {len(results[i])} records")
        except Exception as e:
            errors.append(f"Shard {i+1}: {e}")
            results[i] = []

    threads = [threading.Thread(target=fetch_shard, args=(i, u)) for i, u in enumerate(data_urls)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if errors:
        print("Errors during loading:")
        for err in errors:
            print(f"  - {err}")

    all_textbooks = []
    for r in results:
        if r:
            all_textbooks.extend(r)

    _data_cache["textbooks"] = all_textbooks
    _data_cache["filters"] = extract_filters(all_textbooks)
    _data_cache["loaded"] = True
    print(f"Total: {len(all_textbooks)} textbooks loaded.")


def extract_filters(textbooks):
    """Extract unique filter options from textbook tag_list, sorted by order_num."""
    filters = {}
    for dim_id in DIMENSION_IDS:
        option_orders = {}
        for tb in textbooks:
            for tag in tb.get("tag_list", []):
                if tag.get("tag_dimension_id") == dim_id:
                    name = tag.get("tag_name", "")
                    if not name:
                        continue
                    order = tag.get("order_num", 9999)
                    if name not in option_orders or order < option_orders[name]:
                        option_orders[name] = order
        sorted_options = sorted(option_orders.keys(), key=lambda x: option_orders[x])
        filters[dim_id] = sorted_options
    return filters


def get_tag_value(textbook, dimension_id):
    """Get the tag name for a given dimension from a textbook's tag_list."""
    for tag in textbook.get("tag_list", []):
        if tag.get("tag_dimension_id") == dimension_id:
            return tag.get("tag_name", "")
    return ""


def filter_textbooks(textbooks, params):
    """Filter textbooks based on query parameters (AND between dimensions, OR within)."""
    filter_map = {
        "zxxxd": params.get("xd", ""),
        "zxxxk": params.get("xk", ""),
        "zxxbb": params.get("bb", ""),
        "zxxnj": params.get("nj", ""),
        "zxxcc": params.get("cc", ""),
    }

    result = textbooks
    for dim_id, selected_str in filter_map.items():
        if not selected_str:
            continue
        selected_set = set(s.strip() for s in selected_str.split(",") if s.strip())
        if not selected_set:
            continue
        result = [
            tb for tb in result
            if any(
                tag.get("tag_dimension_id") == dim_id and tag.get("tag_name", "") in selected_set
                for tag in tb.get("tag_list", [])
            )
        ]
    return result


def get_pdf_url(content_id):
    """Get PDF download URL for a textbook by requesting the detail API."""
    if content_id in _data_cache["pdf_url_cache"]:
        return _data_cache["pdf_url_cache"][content_id]

    try:
        resp = requests.get(DETAIL_API.format(content_id=content_id), timeout=30)
        resp.raise_for_status()
        data = resp.json()

        pdf_url = None
        for item in data.get("ti_items", []):
            if item.get("ti_is_source_file") is True:
                storages = item.get("ti_storages", [])
                if storages:
                    # Replace private CDN domain with public CDN
                    pdf_url = re.sub(
                        r"https://r\d-ndr-private\.ykt\.cbern\.com\.cn",
                        "https://c1.ykt.cbern.com.cn",
                        storages[0],
                    )
                elif item.get("ti_storage"):
                    storage = item["ti_storage"]
                    pdf_url = storage.replace(
                        "cs_path:${ref-path}",
                        "https://c1.ykt.cbern.com.cn",
                    )
                break

        _data_cache["pdf_url_cache"][content_id] = pdf_url
        return pdf_url
    except Exception as e:
        print(f"Error fetching PDF URL for {content_id}: {e}")
        _data_cache["pdf_url_cache"][content_id] = None
        return None


def get_textbook_title(content_id):
    """Get textbook title by content_id from cache."""
    for tb in _data_cache["textbooks"]:
        if tb.get("id") == content_id:
            return tb.get("title", "textbook")
    return "textbook"


# ── API Routes ────────────────────────────────────────────────
@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/filters")
def api_filters():
    if not _data_cache["loaded"]:
        return jsonify({"error": "Data not loaded yet"}), 503
    return jsonify({
        "dimensions": DIMENSION_LABELS,
        "options": _data_cache["filters"],
    })


@app.route("/api/textbooks")
def api_textbooks():
    if not _data_cache["loaded"]:
        return jsonify({"error": "Data not loaded yet"}), 503

    filtered = filter_textbooks(_data_cache["textbooks"], request.args)

    # Build response items
    items = []
    for tb in filtered:
        props = tb.get("custom_properties", {})
        providers = tb.get("provider_list", [])
        items.append({
            "id": tb.get("id", ""),
            "title": tb.get("title", ""),
            "xd": get_tag_value(tb, "zxxxd"),
            "xk": get_tag_value(tb, "zxxxk"),
            "bb": get_tag_value(tb, "zxxbb"),
            "nj": get_tag_value(tb, "zxxnj"),
            "cc": get_tag_value(tb, "zxxcc"),
            "size": props.get("size", 0),
            "provider": providers[0].get("name", "") if providers else "",
        })

    return jsonify({"total": len(items), "items": items})


@app.route("/api/pdf-url/<content_id>")
def api_pdf_url(content_id):
    pdf_url = get_pdf_url(content_id)
    if not pdf_url:
        return jsonify({"error": "PDF URL not found"}), 404
    return jsonify({"url": pdf_url})


@app.route("/api/download/<content_id>")
def api_download(content_id):
    pdf_url = get_pdf_url(content_id)
    if not pdf_url:
        return jsonify({"error": "PDF URL not found"}), 404

    title = get_textbook_title(content_id)

    try:
        resp = requests.get(pdf_url, stream=True, timeout=120)
        resp.raise_for_status()

        def generate():
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    yield chunk

        safe_filename = re.sub(r'[\\/:*?"<>|]', '_', title) + ".pdf"
        encoded_filename = urllib.parse.quote(safe_filename)

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
        }
        return Response(generate(), headers=headers, mimetype="application/pdf")
    except Exception as e:
        print(f"Error downloading PDF for {content_id}: {e}")
        return jsonify({"error": f"Download failed: {str(e)}"}), 502


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Electronic Textbook Downloader")
    print("=" * 50)
    print()
    load_data()
    print()
    print("Starting server at http://127.0.0.1:5000")
    print("Press Ctrl+C to stop.")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
