"""
Xiaohongshu Sign Server - Flask service using Playwright to generate X-s/X-t signatures.
Runs on port 5005 independently from the main FastAPI server.
"""
import os
import sys
import time
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SIGN] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global state
_browser = None
_context = None
_page = None
_a1_value = ""
_ready = False


def _init_browser():
    """Initialize Playwright browser with anti-detection."""
    global _browser, _context, _page, _a1_value, _ready

    try:
        from playwright.sync_api import sync_playwright

        stealth_js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stealth.min.js")

        logger.info("Launching Playwright browser...")
        pw = sync_playwright().start()
        _browser = pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        _context = _browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )

        # Load stealth script if available
        if os.path.exists(stealth_js_path):
            logger.info("Loading stealth.min.js...")
            with open(stealth_js_path, "r", encoding="utf-8") as f:
                stealth_js = f.read()
            _context.add_init_script(stealth_js)
        else:
            logger.warning("stealth.min.js not found, using basic anti-detection")

        # Basic anti-detection overrides
        _context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.chrome = { runtime: {} };
        """)

        _page = _context.new_page()
        logger.info("Navigating to xiaohongshu.com...")
        _page.goto("https://www.xiaohongshu.com", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        # Reload to ensure JS is fully loaded
        _page.reload(wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Extract a1 cookie
        cookies = _context.cookies()
        for cookie in cookies:
            if cookie["name"] == "a1":
                _a1_value = cookie["value"]
                logger.info(f"Extracted a1 cookie: {_a1_value[:10]}...")
                break

        # Check if signing function exists
        has_sign_fn = _page.evaluate("() => typeof window._webmsxyw === 'function'")
        if has_sign_fn:
            logger.info("Signing function _webmsxyw found!")
        else:
            logger.warning("Signing function _webmsxyw not found, will try alternative methods")

        _ready = True
        logger.info("Sign server is ready!")

    except Exception as e:
        logger.error(f"Failed to initialize browser: {e}")
        _ready = False


@app.route("/sign", methods=["POST"])
def sign():
    """Generate X-s and X-t signature for a request."""
    if not _ready or _page is None:
        return jsonify({"error": "Sign server not ready"}), 503

    try:
        data = request.json
        uri = data.get("uri", "")
        payload = data.get("data", "") or ""
        a1 = data.get("a1", "")

        # Update a1 cookie in browser if provided
        if a1:
            _context.add_cookies([{"name": "a1", "value": a1, "domain": ".xiaohongshu.com", "path": "/"}])

        # Try primary signing method
        try:
            result = _page.evaluate(
                """([url, data]) => {
                    if (typeof window._webmsxyw === 'function') {
                        const sign = window._webmsxyw(url, data);
                        return { 'X-s': sign['X-s'] || sign['X-s'], 'X-t': String(sign['X-t'] || sign['X-t']) };
                    }
                    return null;
                }""",
                [uri, payload],
            )

            if result and result.get("X-s"):
                return jsonify(result)
        except Exception as e:
            logger.warning(f"Primary sign method failed: {e}")

        # Fallback: try alternative signing approaches
        try:
            result = _page.evaluate(
                """([url, data]) => {
                    // Try to find any signing function on window
                    const keys = Object.keys(window).filter(k => k.startsWith('_'));
                    for (const key of keys) {
                        try {
                            if (typeof window[key] === 'function') {
                                const test = window[key](url, data);
                                if (test && (test['X-s'] || test['X-t'])) {
                                    return { 'X-s': test['X-s'] || '', 'X-t': String(test['X-t'] || '') };
                                }
                            }
                        } catch(e) {}
                    }
                    return null;
                }""",
                [uri, payload],
            )

            if result and result.get("X-s"):
                return jsonify(result)
        except Exception as e:
            logger.warning(f"Alternative sign method failed: {e}")

        # If no browser signing available, return empty (xhs library will use built-in fallback)
        logger.warning("No signing function available, returning empty signature")
        return jsonify({"X-s": "", "X-t": str(int(time.time() * 1000))})

    except Exception as e:
        logger.error(f"Sign error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/a1", methods=["GET"])
def get_a1():
    """Return the current a1 cookie value."""
    return jsonify({"a1": _a1_value})


@app.route("/status", methods=["GET"])
def status():
    """Return server readiness status."""
    return jsonify({"ready": _ready, "a1": bool(_a1_value)})


@app.route("/update_cookie", methods=["POST"])
def update_cookie():
    """Update cookies in the browser context."""
    global _a1_value
    if not _ready or _context is None:
        return jsonify({"error": "Sign server not ready"}), 503

    try:
        cookie_str = request.json.get("cookie", "")
        # Parse cookie string and set in browser
        for part in cookie_str.split(";"):
            kv = part.strip().split("=", 1)
            if len(kv) == 2:
                name = kv[0].strip()
                value = kv[1].strip()
                _context.add_cookies([
                    {"name": name, "value": value, "domain": ".xiaohongshu.com", "path": "/"}
                ])
                if name == "a1":
                    _a1_value = value
                    logger.info(f"Updated a1: {value[:10]}...")

        return jsonify({"status": "ok", "a1": _a1_value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("  Xiaohongshu Sign Server Starting...")
    logger.info("=" * 50)

    # Initialize browser in background
    _init_browser()

    if not _ready:
        logger.error("Browser initialization failed! The server will start but signing may not work.")
        logger.error("Please ensure Playwright is installed: python -m playwright install chromium")

    logger.info("Sign server running on http://0.0.0.0:5005")
    app.run(host="0.0.0.0", port=5005, debug=False, threaded=True)
