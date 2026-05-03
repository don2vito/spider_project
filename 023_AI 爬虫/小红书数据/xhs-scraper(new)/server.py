"""
XHS Data Scraper - Proxy Server
A FastAPI-based proxy server for scraping Xiaohongshu (Little Red Book) notes data.
Features: Playwright browser-assisted signing, anti-anti-crawl, ZIP export, data analysis.

Architecture:
  - Uses Playwright to launch a real Chromium browser
  - Intercepts XHR requests to extract real X-s signatures from XHS's own JS
  - Replays API calls with real signatures via the browser context
  - Falls back to direct API calls with extracted signature headers
"""

import asyncio
import json
import os
import random
import re
import sys
import time
import traceback
import zipfile
from urllib.parse import quote
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

import httpx
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    Response,
    StreamingResponse,
)
from pydantic import BaseModel

# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).parent
SESSION_FILE = BASE_DIR / "xhs_session.json"
XHS_API = "https://edith.xiaohongshu.com"
XHS_WEB = "https://www.xiaohongshu.com"
PORT = 8080

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]


# ============================================================
# Playwright Browser Client
# ============================================================

class BrowserClient:
    """Uses Playwright to navigate XHS pages and intercept API responses."""

    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
        self._ready = False
        self._lock = asyncio.Lock()
        self._init_error = None
        self._headless = True  # Will be set to False if captcha detected

    async def init(self):
        """Initialize browser and navigate to XHS."""
        if self._ready:
            return True
        async with self._lock:
            if self._ready:
                return True
            try:
                from playwright.async_api import async_playwright

                print("[Browser] Launching Chromium browser...")
                pw = await async_playwright().start()
                self._playwright = pw
                self._browser = await pw.chromium.launch(
                    headless=self._headless,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-infobars",
                        "--window-size=1920,1080",
                        "--start-maximized",
                    ],
                )
                self._context = await self._browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent=USER_AGENTS[0],
                    locale="zh-CN",
                    timezone_id="Asia/Shanghai",
                    color_scheme="light",
                )
                # Comprehensive anti-detection scripts
                await self._context.add_init_script("""
                    // 1. Hide webdriver flag
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

                    // 2. Mock plugins (real browsers have plugins)
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => {
                            const plugins = [
                                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
                                {name: 'Native Client', filename: 'internal-nacl-plugin', description: ''}
                            ];
                            plugins.length = 3;
                            return plugins;
                        }
                    });

                    // 3. Mock languages
                    Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});

                    // 4. Mock platform
                    Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});

                    // 5. Mock hardware concurrency
                    Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});

                    // 6. Mock device memory
                    Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});

                    // 7. Override permissions query
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) =>
                        parameters.name === 'notifications'
                            ? Promise.resolve({state: Notification.permission})
                            : originalQuery(parameters);

                    // 8. Mock chrome object
                    window.chrome = {runtime: {}, loadTimes: function(){}, csi: function(){}};

                    // 9. Remove automation-related properties
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                """)
                self._page = await self._context.new_page()

                # Inject cookies before navigating
                session_file = SESSION_FILE
                if session_file.exists():
                    try:
                        data = json.loads(session_file.read_text(encoding="utf-8"))
                        cookies = data.get("cookies", {})
                        if cookies:
                            cookie_list = []
                            for k, v in cookies.items():
                                cookie_list.append({
                                    "name": k,
                                    "value": v,
                                    "domain": ".xiaohongshu.com",
                                    "path": "/",
                                })
                            await self._context.add_cookies(cookie_list)
                            print(f"[Browser] Injected {len(cookie_list)} cookies")
                    except Exception as e:
                        print(f"[Browser] Failed to inject cookies: {e}")

                # Navigate to XHS homepage to load all JS
                print("[Browser] Navigating to xiaohongshu.com...")
                await self._page.goto(XHS_WEB, wait_until="domcontentloaded", timeout=30000)
                await self._page.wait_for_timeout(3000)
                print("[Browser] Browser ready!")
                self._ready = True
                return True
            except ImportError:
                self._init_error = "playwright not installed. Run: pip install playwright && playwright install chromium"
                print(f"[Browser] ERROR: {self._init_error}")
                return False
            except Exception as e:
                self._init_error = str(e)
                print(f"[Browser] ERROR: Failed to init: {e}")
                return False

    async def _ensure_ready(self):
        if not self._ready:
            ok = await self.init()
            if not ok:
                raise RuntimeError(f"Browser not available: {self._init_error}")
        try:
            await self._page.evaluate("1+1")
        except Exception:
            print("[Browser] Page lost, reinitializing...")
            self._ready = False
            await self.close()
            ok = await self.init()
            if not ok:
                raise RuntimeError(f"Browser re-init failed: {self._init_error}")

    async def _check_captcha_and_wait(self, page_url: str) -> bool:
        """Check if current page is a captcha page. If so, wait for user to solve it.
        Returns True if captcha was detected and we need to retry.
        Distinguishes between:
          - Real captcha: /website-login/captcha?verifyType=...
          - Note unavailable: /404?source=/404/sec_xxx (not a captcha, just content restriction)
        """
        current_url = self._page.url
        # Only treat specific captcha URLs as captcha — NOT /404/sec_xxx pages
        is_captcha = (
            "/website-login/captcha" in current_url
            or ("captcha" in current_url and "verifyType" in current_url)
        )
        if is_captcha:
            print(f"[Browser] ⚠️ CAPTCHA detected! URL: {current_url[:80]}...")
            if self._headless:
                print("[Browser] Switching to headed mode (visible browser) for captcha solving...")
                # Close current browser and reopen in headed mode
                self._headless = False
                self._ready = False
                await self.close()
                ok = await self.init()
                if not ok:
                    return False
                # Re-navigate to the target page
                await self._page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
                await self._page.wait_for_timeout(2000)
                current_url = self._page.url

            # Re-check after potential headed mode switch
            is_captcha = (
                "/website-login/captcha" in current_url
                or ("captcha" in current_url and "verifyType" in current_url)
            )
            if is_captcha:
                print("[Browser] ⏳ Please solve the captcha in the browser window...")
                print("[Browser] Waiting for captcha to be solved (max 120 seconds)...")
                # Wait for user to solve captcha (check every 2 seconds, max 120s)
                for i in range(60):
                    await self._page.wait_for_timeout(2000)
                    current_url = self._page.url
                    is_still_captcha = (
                        "/website-login/captcha" in current_url
                        or ("captcha" in current_url and "verifyType" in current_url)
                    )
                    if not is_still_captcha:
                        print("[Browser] ✅ Captcha solved! Continuing...")
                        await self._page.wait_for_timeout(2000)
                        return True
                print("[Browser] ⏰ Captcha solve timeout (120s)")
                return False
        return False

    async def intercept_api(self, url_pattern: str, page_url: str, wait_ms: int = 15000) -> dict:
        """
        Navigate to page_url and intercept the first API response matching url_pattern.
        Returns the parsed JSON response body.
        """
        await self._ensure_ready()

        result_holder = {"data": None, "found": False}

        async def on_response(response):
            if result_holder["found"]:
                return
            resp_url = response.url
            if url_pattern in resp_url:
                try:
                    body = await response.json()
                    result_holder["data"] = body
                    result_holder["found"] = True
                    print(f"[Browser] Intercepted API: {resp_url[:80]}...")
                except Exception:
                    pass  # Not JSON, skip

        self._page.on("response", on_response)

        try:
            await self._page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
            # Wait for the API response to be intercepted
            for _ in range(int(wait_ms / 500)):
                if result_holder["found"]:
                    break
                await self._page.wait_for_timeout(500)
            else:
                # Also try scrolling to trigger lazy loading
                await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self._page.wait_for_timeout(3000)
        finally:
            self._page.remove_listener("response", on_response)

        if result_holder["found"]:
            return result_holder["data"]
        return None

    async def intercept_api_scroll(self, url_pattern: str, base_url: str, max_scrolls: int = 50) -> list:
        """
        Navigate to base_url and keep scrolling to intercept multiple API responses.
        Returns a list of all parsed JSON response bodies.
        """
        await self._ensure_ready()

        all_results = []
        seen_cursors = set()
        all_api_urls = []  # Debug: track all API URLs seen

        async def on_response(response):
            resp_url = response.url
            # Debug: log all API calls
            if "/api/" in resp_url and "xiaohongshu" in resp_url:
                all_api_urls.append(resp_url)
                print(f"[Browser] API call: {resp_url[:100]}")
            if url_pattern in resp_url:
                try:
                    body = await response.json()
                    # Deduplicate by cursor
                    cursor = str(body.get("data", {}).get("cursor", ""))
                    if cursor not in seen_cursors:
                        seen_cursors.add(cursor)
                        all_results.append(body)
                        notes = body.get("data", {}).get("notes", [])
                        has_more = body.get("data", {}).get("has_more", False)
                        print(f"[Browser] Intercepted page {len(all_results)}: {len(notes)} notes, has_more={has_more}")
                except Exception:
                    pass

        self._page.on("response", on_response)

        try:
            print(f"[Browser] Navigating to: {base_url}")
            resp = await self._page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            final_url = self._page.url
            print(f"[Browser] Final URL: {final_url}")
            print(f"[Browser] Response status: {resp.status if resp else 'N/A'}")

            # Check if redirected to login/explore page
            if "/login" in final_url or "/explore" in final_url:
                print(f"[Browser] WARNING: Page redirected to {final_url} — may need login or xsec_token")

            await self._page.wait_for_timeout(3000)

            # Debug: log page title
            title = await self._page.title()
            print(f"[Browser] Page title: {title}")

            # Scroll down to load more notes
            for i in range(max_scrolls):
                prev_count = len(all_results)
                await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self._page.wait_for_timeout(2000)

                # Check if we got new data
                if len(all_results) == prev_count:
                    # No new data, try one more scroll with longer wait
                    await self._page.wait_for_timeout(2000)
                    if len(all_results) == prev_count:
                        break

                # Check if last response says no more
                if all_results:
                    last = all_results[-1]
                    if not last.get("data", {}).get("has_more", False):
                        print(f"[Browser] No more pages after {len(all_results)} pages")
                        break
        finally:
            self._page.remove_listener("response", on_response)

        # Debug: if no results, print all API URLs we saw
        if not all_results:
            print(f"[Browser] No matching responses intercepted. Total API calls seen: {len(all_api_urls)}")
            for u in all_api_urls[:20]:
                print(f"  - {u}")
            if not all_api_urls:
                print("[Browser] No API calls detected at all. Page may not have loaded properly.")

        return all_results

    async def update_cookies(self, cookies: dict):
        if not self._context:
            return
        try:
            cookie_list = []
            for k, v in cookies.items():
                cookie_list.append({
                    "name": k,
                    "value": v,
                    "domain": ".xiaohongshu.com",
                    "path": "/",
                })
            await self._context.add_cookies(cookie_list)
            print(f"[Browser] Updated {len(cookie_list)} cookies")
        except Exception as e:
            print(f"[Browser] Failed to update cookies: {e}")

    async def get_page_cookies(self) -> dict:
        if not self._context:
            return {}
        try:
            cookies = await self._context.cookies()
            return {c["name"]: c["value"] for c in cookies}
        except Exception:
            return {}

    async def close(self):
        try:
            if self._page:
                await self._page.close()
        except Exception:
            pass
        try:
            if self._context:
                await self._context.close()
        except Exception:
            pass
        try:
            if self._browser:
                await self._browser.close()
        except Exception:
            pass
        try:
            if hasattr(self, '_playwright') and self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        self._browser = None
        self._context = None
        self._page = None
        self._ready = False


# ============================================================
# Session Manager - Cookie/Session management
# ============================================================

class SessionManager:
    """Manages XHS login session (cookies)."""

    def __init__(self):
        self.cookies: dict = {}
        self.user_agent: str = random.choice(USER_AGENTS)
        self._load()

    @property
    def a1(self) -> Optional[str]:
        return self.cookies.get("a1", "")

    @property
    def is_logged_in(self) -> bool:
        return bool(self.cookies.get("web_session"))

    def _load(self):
        if SESSION_FILE.exists():
            try:
                data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
                self.cookies = data.get("cookies", {})
                self.user_agent = data.get("user_agent", self.user_agent)
                print(f"[Session] Loaded {len(self.cookies)} cookies from file")
            except Exception as e:
                print(f"[Session] Failed to load session: {e}")

    def save(self):
        data = {
            "cookies": self.cookies,
            "user_agent": self.user_agent,
            "saved_at": time.time(),
        }
        SESSION_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def set_cookies(self, cookie_str: str):
        """Parse and set cookies from browser cookie string."""
        self.cookies = {}
        for item in cookie_str.split(";"):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                self.cookies[key.strip()] = value.strip()
        self.save()
        print(f"[Session] Set {len(self.cookies)} cookies, a1={'yes' if self.a1 else 'no'}")

    def get_cookie_header(self) -> str:
        return "; ".join(f"{k}={v}" for k, v in self.cookies.items())

    def rotate_ua(self):
        self.user_agent = random.choice(USER_AGENTS)


# ============================================================
# XHS API Client (Browser-assisted)
# ============================================================

class XHSClient:
    """Async HTTP client for XHS API using browser page navigation + SSR data extraction."""

    def __init__(self, session: SessionManager, browser: BrowserClient):
        self.session = session
        self.browser = browser

    @staticmethod
    def _clean_json_string(json_str: str) -> str:
        """Clean a JSON string by replacing undefined/NaN/Infinity only outside of string literals."""
        result = []
        in_string = False
        escape_next = False
        i = 0
        while i < len(json_str):
            ch = json_str[i]
            if escape_next:
                result.append(ch)
                escape_next = False
                i += 1
                continue
            if ch == '\\' and in_string:
                result.append(ch)
                escape_next = True
                i += 1
                continue
            if ch == '"':
                in_string = not in_string
                result.append(ch)
                i += 1
                continue
            if in_string:
                result.append(ch)
                i += 1
                continue
            # Outside string — check for undefined, NaN, Infinity
            if json_str[i:i+9] == 'undefined':
                result.append('null')
                i += 9
                continue
            if json_str[i:i+3] == 'NaN':
                result.append('0')
                i += 3
                continue
            if json_str[i:i+8] == 'Infinity':
                result.append('0')
                i += 8
                continue
            result.append(ch)
            i += 1
        return ''.join(result)

    async def _extract_ssr_data(self, page_url: str, wait_ms: int = 10000) -> dict:
        """Navigate to page and extract SSR data from page."""
        await self.browser._ensure_ready()
        page = self.browser._page

        print(f"[Client] Navigating to: {page_url}")
        resp = await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
        final_url = page.url
        print(f"[Client] Final URL: {final_url}")
        print(f"[Client] Response status: {resp.status if resp else 'N/A'}")

        # Check for captcha redirect
        captcha_detected = await self.browser._check_captcha_and_wait(page_url)
        if captcha_detected:
            # Captcha was solved, re-navigate to get actual page
            print(f"[Client] Re-navigating after captcha solve...")
            resp = await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
            final_url = page.url
            print(f"[Client] Final URL after retry: {final_url}")

        # Check again if still on captcha page
        is_captcha = (
            "/website-login/captcha" in page.url
            or ("captcha" in page.url and "verifyType" in page.url)
        )
        if is_captcha:
            print(f"[Client] Still on captcha page, giving up")
            return {}

        # Check if page redirected to 404 (note unavailable) — not a captcha
        if "/404" in page.url and "error_code" in page.url:
            print(f"[Client] Note unavailable (404 page), returning empty data")
            return {}

        # Wait for page HTML to be fully loaded
        await page.wait_for_timeout(2000)

        # Strategy: Get the raw script tag content containing __INITIAL_STATE__
        # and parse it in Python. This avoids:
        # 1. Vue Proxy circular reference issues (can't JSON.stringify in JS)
        # 2. JS regex truncation issues (nested braces in JSON)
        # 3. JSON.parse("...") escaping issues
        script_contents = await page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script');
                const results = [];
                for (const s of scripts) {
                    const text = s.textContent || '';
                    if (text.includes('__INITIAL_STATE__')) {
                        results.push(text);
                    }
                }
                return results;
            }
        """)

        if not script_contents:
            print("[Client] No script tag with __INITIAL_STATE__ found")
            return {}

        # Parse the script content in Python to extract the JSON
        import re
        for script_text in script_contents:
            # Method 1: window.__INITIAL_STATE__=JSON.parse("...")
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*JSON\.parse\("((?:[^"\\]|\\.)*)"\)', script_text, re.DOTALL)
            if match:
                raw_json = match.group(1)
                # Unescape JSON string escapes
                raw_json = raw_json.replace('\\"', '"').replace('\\\\n', '\n').replace('\\\\t', '\t').replace('\\\\\\\\"', '\\"').replace('\\\\\\\\', '\\\\')
                try:
                    data = json.loads(raw_json)
                    print(f"[Client] SSR data extracted (JSON.parse method), keys: {list(data.keys())[:15]}")
                    return data
                except json.JSONDecodeError as e:
                    print(f"[Client] JSON.parse method failed: {e}")
                    # Try cleanup
                    try:
                        cleaned = raw_json.replace('undefined', 'null').replace('NaN', '0').replace('Infinity', '0')
                        data = json.loads(cleaned)
                        print(f"[Client] SSR data extracted after cleanup, keys: {list(data.keys())[:15]}")
                        return data
                    except json.JSONDecodeError as e2:
                        print(f"[Client] Cleanup also failed: {e2}")
                    continue

            # Method 2: window.__INITIAL_STATE__={...}  (direct object)
            # Find the = sign and extract everything after it
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*', script_text)
            if match:
                json_start = match.end()
                json_str = script_text[json_start:].rstrip()
                # Remove trailing semicolons and whitespace
                json_str = json_str.rstrip().rstrip(';').rstrip()
                # Handle JSON.parse("...") wrapper
                jp_match = re.match(r'^JSON\.parse\("(.*)"\)$', json_str, re.DOTALL)
                if jp_match:
                    json_str = jp_match.group(1)
                    json_str = json_str.replace('\\"', '"').replace('\\\\n', '\n').replace('\\\\t', '\t')

                # Try to find the balanced JSON object
                # Count braces to find the end of the object
                if json_str.startswith('{'):
                    depth = 0
                    in_string = False
                    escape_next = False
                    end_idx = 0
                    for i, ch in enumerate(json_str):
                        if escape_next:
                            escape_next = False
                            continue
                        if ch == '\\' and in_string:
                            escape_next = True
                            continue
                        if ch == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        if in_string:
                            continue
                        if ch == '{':
                            depth += 1
                        elif ch == '}':
                            depth -= 1
                            if depth == 0:
                                end_idx = i + 1
                                break
                    if end_idx > 0:
                        json_str = json_str[:end_idx]

                try:
                    data = json.loads(json_str)
                    print(f"[Client] SSR data extracted (direct object method), keys: {list(data.keys())[:15]}")
                    return data
                except json.JSONDecodeError as e:
                    print(f"[Client] Direct object parse failed at char {e.pos}: {e}")
                    # Show context around the error position
                    start = max(0, e.pos - 50)
                    end = min(len(json_str), e.pos + 50)
                    print(f"[Client] Context around error: ...{json_str[start:end]}...")
                    try:
                        # Smart cleanup: only replace undefined/NaN outside of strings
                        cleaned = self._clean_json_string(json_str)
                        data = json.loads(cleaned)
                        print(f"[Client] SSR data extracted after cleanup, keys: {list(data.keys())[:15]}")
                        # Debug: inspect user.notes structure
                        try:
                            notes_raw = data.get("user", {}).get("notes", [])
                            print(f"[Client] user.notes type: {type(notes_raw).__name__}, len: {len(notes_raw)}")
                            for idx, item in enumerate(notes_raw[:2]):
                                if isinstance(item, dict):
                                    print(f"[Client]   note[{idx}] keys: {list(item.keys())[:15]}")
                                    # Print first 300 chars of each value
                                    for k, v in list(item.items())[:5]:
                                        print(f"[Client]   note[{idx}].{k} = {str(v)[:100]}")
                                else:
                                    print(f"[Client]   note[{idx}] type: {type(item).__name__}, value: {str(item)[:100]}")
                        except Exception as dbg_e:
                            print(f"[Client] Debug error: {dbg_e}")
                        return data
                    except json.JSONDecodeError as e2:
                        print(f"[Client] All parse methods failed: {e2}")
                        # Print a sample of the JSON for debugging
                        print(f"[Client] JSON starts with: {json_str[:200]}")
                        print(f"[Client] JSON ends with: {json_str[-200:]}")
                    continue

        print("[Client] SSR extraction failed, will use DOM extraction as fallback")
        return {}

    async def get_user_notes(self, user_id: str, on_progress=None) -> list:
        """Fetch all notes by navigating to user profile, extracting SSR data, then scrolling for more."""
        profile_url = f"{XHS_WEB}/user/profile/{user_id}"
        print(f"[Client] Fetching notes for user: {user_id}")

        # Step 1: Navigate and extract initial SSR data
        ssr_data = await self._extract_ssr_data(profile_url)

        if not ssr_data:
            raise HTTPException(
                status_code=401,
                detail="无法获取页面数据。可能原因：Cookie已失效、需要登录、或触发了反爬验证。请重新配置Cookie后重试。"
            )

        # Step 2: Extract notes from SSR data
        all_notes = []
        notes_data = self._extract_notes_from_ssr(ssr_data)
        all_notes.extend(notes_data)
        print(f"[Client] SSR: extracted {len(notes_data)} notes")

        if on_progress:
            on_progress(len(all_notes), 1)

        # Step 3: Scroll to load more notes and intercept API responses
        page = self.browser._page
        seen_note_ids = {n.get("note_id", n.get("id", "")) for n in all_notes}
        additional_notes = []

        async def on_response(response):
            resp_url = response.url
            # Watch for any API that might return notes
            if "edith.xiaohongshu.com" in resp_url and "/api/" in resp_url:
                try:
                    body = await response.json()
                    if isinstance(body, dict) and body.get("success"):
                        data = body.get("data", {})
                        # Could be user_posted or homefeed format
                        notes = data.get("notes", [])
                        items = data.get("items", [])
                        if notes:
                            for n in notes:
                                nid = n.get("note_id", n.get("id", ""))
                                if nid and nid not in seen_note_ids:
                                    seen_note_ids.add(nid)
                                    additional_notes.append(n)
                                    print(f"[Client] Scroll: intercepted new note {nid[:12]}...")
                        if items:
                            for item in items:
                                note_data = item.get("note_data", item)
                                nid = note_data.get("note_id", note_data.get("id", ""))
                                if nid and nid not in seen_note_ids:
                                    seen_note_ids.add(nid)
                                    additional_notes.append(note_data)
                                    print(f"[Client] Scroll: intercepted new note {nid[:12]}...")
                except Exception:
                    pass

        page.on("response", on_response)

        try:
            # Check if there are more notes to load (SSR usually has first page)
            has_more = self._check_has_more(ssr_data)
            if has_more:
                print(f"[Client] More notes available, scrolling to load...")
                for i in range(100):
                    prev_total = len(all_notes) + len(additional_notes)
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2500)

                    # Also try extracting newly rendered notes from DOM
                    dom_notes = await self._extract_notes_from_dom(page)
                    for n in dom_notes:
                        nid = n.get("note_id", n.get("id", ""))
                        if nid and nid not in seen_note_ids:
                            seen_note_ids.add(nid)
                            additional_notes.append(n)

                    new_total = len(all_notes) + len(additional_notes)
                    if new_total == prev_total:
                        # No new notes after scroll, wait longer
                        await page.wait_for_timeout(2000)
                        if len(all_notes) + len(additional_notes) == prev_total:
                            break

                    if on_progress:
                        on_progress(len(all_notes) + len(additional_notes), i + 2)
        finally:
            page.remove_listener("response", on_response)

        all_notes.extend(additional_notes)
        print(f"[Client] Total notes fetched: {len(all_notes)}")
        return all_notes

    def _extract_notes_from_ssr(self, ssr_data: dict) -> list:
        """Extract notes from raw SSR JSON data.
        
        user.notes is a 2D array (masonry grid rows/columns):
          [[{id, noteCard: {noteId, xsecToken, title, desc, ...}}, ...], [], ...]
        """
        notes = []

        user_data = ssr_data.get("user", {})
        notes_grid = user_data.get("notes", [])

        if not notes_grid or not isinstance(notes_grid, list):
            print(f"[Client] user.notes is empty or not a list")
            return []

        print(f"[Client] user.notes: {len(notes_grid)} rows in grid")

        for row_idx, row in enumerate(notes_grid):
            if not isinstance(row, list):
                continue
            for item in row:
                if not isinstance(item, dict):
                    continue
                # The actual note data is inside noteCard
                note_card = item.get("noteCard", {})
                if not isinstance(note_card, dict) or not note_card:
                    continue

                # Debug first note
                if not notes:
                    print(f"[Client] First noteCard keys: {list(note_card.keys())[:20]}")

                notes.append(note_card)

        print(f"[Client] Extracted {len(notes)} notes from grid")
        return notes

    def _check_has_more(self, ssr_data: dict) -> bool:
        """Check if SSR data indicates more notes are available."""
        try:
            user_data = ssr_data.get("user", {})
            # Check noteQueries for pagination info
            queries = user_data.get("noteQueries", {})
            if isinstance(queries, dict):
                cursor = queries.get("cursor", "")
                has_more = queries.get("has_more", False)
                if has_more or cursor:
                    return True
            # Also check if notes list length matches a typical page size
            notes = user_data.get("notes", [])
            if isinstance(notes, list) and len(notes) >= 16:
                return True
        except (AttributeError, TypeError):
            pass
        return False

    async def _extract_notes_from_dom(self, page) -> list:
        """Extract note data from DOM elements rendered by scrolling."""
        try:
            notes_json = await page.evaluate("""
                () => {
                    const notes = [];
                    // Find all note card elements
                    const noteCards = document.querySelectorAll('section.note-item, div.note-item, a[href*="/explore/"], a[href*="/discovery/item/"]');
                    for (const card of noteCards) {
                        const link = card.querySelector('a[href*="/explore/"], a[href*="/discovery/item/"]') || card;
                        const href = link.getAttribute('href') || '';
                        const match = href.match(/\\/explore\\/([a-f0-9]+)/) || href.match(/\\/discovery\\/item\\/([a-f0-9]+)/);
                        if (match) {
                            const noteId = match[1];
                            const titleEl = card.querySelector('span.title, div.title, a.title');
                            const imgEl = card.querySelector('img');
                            notes.push({
                                note_id: noteId,
                                id: noteId,
                                display_title: titleEl ? titleEl.textContent.trim() : '',
                                title: titleEl ? titleEl.textContent.trim() : '',
                                cover_url: imgEl ? imgEl.getAttribute('src') : '',
                                type: 'normal',
                            });
                        }
                    }
                    return JSON.stringify(notes);
                }
            """)
            if notes_json:
                notes = json.loads(notes_json)
                if notes:
                    print(f"[Client] DOM: found {len(notes)} note cards")
                return notes
        except Exception as e:
            print(f"[Client] DOM extraction error: {e}")
        return []

    async def get_user_info(self, user_id: str) -> dict:
        """Fetch user info from SSR data on profile page."""
        profile_url = f"{XHS_WEB}/user/profile/{user_id}"
        print(f"[Client] Fetching user info: {user_id}")

        ssr_data = await self._extract_ssr_data(profile_url)
        if not ssr_data:
            return {}

        # Try user.userPageData (Vue SSR store structure)
        user_data = ssr_data.get("user", {})
        page_data = user_data.get("userPageData", {})
        if isinstance(page_data, dict) and page_data:
            print(f"[Client] Got userPageData, keys: {list(page_data.keys())[:10]}")
            return page_data

        # Try user.userInfo
        user_info = user_data.get("userInfo", {})
        if isinstance(user_info, dict) and user_info:
            return user_info

        return {}

    async def get_note_detail(self, note_id: str, xsec_token: str = "") -> dict:
        """Fetch note detail from SSR data on note page."""
        note_url = f"{XHS_WEB}/explore/{note_id}"
        if xsec_token:
            note_url += f"?xsec_token={xsec_token}&xsec_source=pc_user"
        print(f"[Client] Fetching note detail: {note_id}")

        ssr_data = await self._extract_ssr_data(note_url)
        if not ssr_data:
            return {}

        # Extract note from SSR data
        try:
            note_data = ssr_data.get("note", {})
            note_detail = note_data.get("noteDetailMap", {})
            if note_detail:
                # noteDetailMap is keyed by note_id
                for k, v in note_detail.items():
                    note = v.get("note", v)
                    if note:
                        return note
        except (AttributeError, TypeError):
            pass

        # Try firstNoteList
        try:
            note_data = ssr_data.get("note", {})
            first_list = note_data.get("firstNoteList", [])
            if first_list:
                item = first_list[0]
                note = item.get("note", item)
                if note:
                    return note
        except (AttributeError, TypeError):
            pass

        return {}

    async def get_note_comments(self, note_id: str, xsec_token: str = "") -> list:
        """Fetch comments from SSR data + API interception on note page."""
        note_url = f"{XHS_WEB}/explore/{note_id}"
        if xsec_token:
            note_url += f"?xsec_token={xsec_token}&xsec_source=pc_user"
        print(f"[Client] Fetching comments for: {note_id}")

        all_comments = []
        seen_ids = set()
        api_comments = []
        page = self.browser._page

        # Step 1: Set up API interceptor BEFORE navigating
        async def on_response(response):
            resp_url = response.url
            if "/comment/" in resp_url and ("edith.xiaohongshu.com" in resp_url or "edith.xhscdn.com" in resp_url):
                try:
                    body = await response.json()
                    if isinstance(body, dict) and body.get("success"):
                        data = body.get("data", {})
                        comments = data.get("comments", [])
                        for c in comments:
                            cid = c.get("id", "")
                            if cid and cid not in seen_ids:
                                seen_ids.add(cid)
                                api_comments.append(c)
                except Exception:
                    pass

        page.on("response", on_response)

        try:
            # Step 2: Navigate to note page (API responses will be captured)
            ssr_data = await self._extract_ssr_data(note_url)

            # Step 3: Extract comments from SSR data
            if ssr_data:
                try:
                    note_data = ssr_data.get("note", {})

                    # Path 1: noteDetailMap[noteId].comments.list (XHS current SSR structure)
                    detail_map = note_data.get("noteDetailMap", {})
                    if isinstance(detail_map, dict) and detail_map:
                        for map_key, map_val in detail_map.items():
                            if not isinstance(map_val, dict):
                                continue
                            comments_obj = map_val.get("comments", {})
                            if not isinstance(comments_obj, dict):
                                continue
                            comments_list = comments_obj.get("list", [])
                            if isinstance(comments_list, list) and comments_list:
                                if not all_comments:
                                    print(f"[Client] SSR: found comments in noteDetailMap.comments.list, len={len(comments_list)}")
                                for c in comments_list:
                                    if not isinstance(c, dict):
                                        continue
                                    cid = c.get("id") or c.get("commentId") or ""
                                    if cid and cid not in seen_ids:
                                        seen_ids.add(cid)
                                        parsed = self._parse_comment(c)
                                        all_comments.append(parsed)
                                        for sub in parsed.get("sub_comments", []):
                                            sub_id = sub.get("id", "")
                                            if sub_id:
                                                seen_ids.add(sub_id)
                                break

                    # Path 2: note.commentData.comments (older SSR structure)
                    if not all_comments:
                        comment_data = note_data.get("commentData", {})
                        if isinstance(comment_data, dict) and comment_data:
                            comments_list = comment_data.get("comments", [])
                            if isinstance(comments_list, list) and comments_list:
                                print(f"[Client] SSR: found comments in note.commentData.comments, len={len(comments_list)}")
                                for c in comments_list:
                                    if not isinstance(c, dict):
                                        continue
                                    cid = c.get("id") or c.get("commentId") or ""
                                    if cid and cid not in seen_ids:
                                        seen_ids.add(cid)
                                        all_comments.append(self._parse_comment(c))

                except (AttributeError, TypeError) as e:
                    print(f"[Client] SSR comment parse error: {e}")
                    traceback.print_exc()

            # Step 4: Scroll to load more comments via API
            for _ in range(10):
                prev = len(all_comments) + len(api_comments)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
                if len(all_comments) + len(api_comments) == prev:
                    break

        finally:
            page.remove_listener("response", on_response)

        # Parse API comments
        for c in api_comments:
            all_comments.append(self._parse_comment(c))

        print(f"[Client] Total comments: {len(all_comments)} (SSR: {len(all_comments) - len(api_comments)}, API: {len(api_comments)})")
        return all_comments

    @staticmethod
    def _parse_comment(c: dict) -> dict:
        """Parse a comment object into standard format.
        Handles both SSR format (user.nickname) and API format (user_info.nickname).
        """
        # User info — SSR uses c.user, API uses c.user_info
        user_obj = c.get("user") or c.get("user_info") or {}
        if not isinstance(user_obj, dict):
            user_obj = {}
        nickname = user_obj.get("nickname") or user_obj.get("nickName") or "Anonymous"
        user_id = user_obj.get("userId") or user_obj.get("user_id") or ""

        # Target comment (for replies) — SSR uses c.targetComment, API uses c.target_comment
        target_obj = c.get("targetComment") or c.get("target_comment") or {}
        if not isinstance(target_obj, dict):
            target_obj = {}
        target_user = target_obj.get("user") or target_obj.get("user_info") or {}
        if not isinstance(target_user, dict):
            target_user = {}
        target_nickname = target_user.get("nickname") or target_user.get("nickName") or ""

        # Content
        content = c.get("content") or ""
        # SSR may have content in different field
        if not content:
            content = c.get("commentContent") or c.get("text") or ""

        # Like count
        like_count = c.get("likeCount") or c.get("like_count") or 0

        # IP location
        ip_location = c.get("ipLocation") or c.get("ip_location") or ""

        # Create time — could be timestamp (ms) or formatted string
        create_time = c.get("createTime") or c.get("create_time") or c.get("time") or 0
        if isinstance(create_time, (int, float)) and create_time > 0:
            try:
                from datetime import datetime as dt
                create_time = dt.fromtimestamp(int(create_time) / 1000).strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, OSError, TypeError):
                create_time = str(create_time)

        # Sub-comments / replies
        sub_comments = c.get("subComments") or c.get("sub_comments") or []
        if not isinstance(sub_comments, list):
            sub_comments = []
        parsed_subs = []
        for sub in sub_comments:
            parsed_subs.append(XHSClient._parse_comment(sub))

        return {
            "id": c.get("id") or c.get("commentId") or "",
            "user": nickname,
            "user_id": user_id,
            "content": content,
            "like_count": like_count,
            "ip_location": ip_location,
            "create_time": str(create_time) if create_time else "",
            "target_user": target_nickname,
            "sub_comments": parsed_subs,
        }

    async def download_file(self, url: str) -> bytes:
        """Download a file (image/video) from URL."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "User-Agent": self.session.user_agent,
                "Referer": XHS_WEB + "/",
            }
            if self.session.cookies:
                headers["Cookie"] = self.session.get_cookie_header()
            resp = await client.get(url, headers=headers)
            return resp.content

    async def close(self):
        await self.browser.close()


# ============================================================
# Data Analyzer
# ============================================================

class DataAnalyzer:
    """Analyze scraped XHS notes data."""

    def __init__(self, notes: list):
        self.notes = notes
        self.df = self._build_dataframe()

    def _build_dataframe(self) -> pd.DataFrame:
        rows = []
        for n in self.notes:
            # Support both noteCard (camelCase) and detail (snake_case) formats
            interact = n.get("interact_info") or n.get("interactInfo") or {}
            if not isinstance(interact, dict):
                interact = {}
            image_list = n.get("image_list") or n.get("imageList") or []
            if not isinstance(image_list, list):
                image_list = []
            tag_list = n.get("tag_list") or n.get("tagList") or []
            if not isinstance(tag_list, list):
                tag_list = []
            video = n.get("video") or {}

            # Interact counts — camelCase (likedCount) or snake_case (liked_count)
            liked = interact.get("likedCount") or interact.get("liked_count") or "0"
            collected = interact.get("collectedCount") or interact.get("collected_count") or "0"
            comment = interact.get("commentCount") or interact.get("comment_count") or "0"
            share = interact.get("shareCount") or interact.get("share_count") or "0"

            rows.append({
                "note_id": n.get("note_id") or n.get("noteId") or n.get("id") or "",
                "title": n.get("display_title") or n.get("displayTitle") or n.get("title") or "",
                "type": n.get("type", "normal"),
                "time": n.get("time") or n.get("timestamp") or 0,
                "liked_count": self._parse_num(liked),
                "collected_count": self._parse_num(collected),
                "comment_count": self._parse_num(comment),
                "share_count": self._parse_num(share),
                "image_count": len(image_list),
                "has_video": bool(video),
                "tag_list": [t.get("name", t) if isinstance(t, dict) else t for t in tag_list if t],
                "desc_length": len(n.get("desc") or ""),
            })
        return pd.DataFrame(rows)

    @staticmethod
    def _parse_num(val) -> int:
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, str):
            val = val.replace(",", "").strip()
            if val.endswith("万"):
                return int(float(val[:-1]) * 10000)
            if val.endswith("亿"):
                return int(float(val[:-1]) * 100000000)
            try:
                return int(val)
            except ValueError:
                return 0
        return 0

    def analyze(self) -> dict:
        """Generate comprehensive analysis report."""
        if self.df.empty:
            return {"error": "No data to analyze"}

        df = self.df.copy()
        df["date"] = pd.to_datetime(df["time"], unit="ms", errors="coerce")
        df["engagement_rate"] = (
            (df["liked_count"] + df["collected_count"] + df["comment_count"])
            / df[["liked_count", "collected_count", "comment_count"]].max().max().clip(lower=1)
            * 100
        )

        # 1. Summary statistics
        summary = {
            "total_notes": len(df),
            "avg_likes": round(df["liked_count"].mean(), 1),
            "avg_collects": round(df["collected_count"].mean(), 1),
            "avg_comments": round(df["comment_count"].mean(), 1),
            "total_likes": int(df["liked_count"].sum()),
            "total_collects": int(df["collected_count"].sum()),
            "total_comments": int(df["comment_count"].sum()),
            "video_count": int(df["has_video"].sum()),
            "image_note_count": int((~df["has_video"]).sum()),
            "avg_images": round(df["image_count"].mean(), 1),
            "avg_desc_length": round(df["desc_length"].mean(), 1),
        }

        # Date range
        valid_dates = df["date"].dropna()
        if not valid_dates.empty:
            summary["earliest_note"] = valid_dates.min().strftime("%Y-%m-%d")
            summary["latest_note"] = valid_dates.max().strftime("%Y-%m-%d")
            summary["date_span_days"] = (valid_dates.max() - valid_dates.min()).days

        # 2. Top 10 by likes
        top_likes = df.nlargest(10, "liked_count")[["title", "liked_count", "note_id"]].to_dict("records")

        # 3. Top 10 by collects
        top_collects = df.nlargest(10, "collected_count")[["title", "collected_count", "note_id"]].to_dict("records")

        # 4. Top 10 by comments
        top_comments = df.nlargest(10, "comment_count")[["title", "comment_count", "note_id"]].to_dict("records")

        # 5. Content type distribution
        type_dist = df["has_video"].value_counts().to_dict()
        content_type = {
            "image_notes": int(type_dist.get(False, 0)),
            "video_notes": int(type_dist.get(True, 0)),
        }

        # 6. Monthly trend
        if not valid_dates.empty:
            df["month"] = df["date"].dt.to_period("M").astype(str)
            monthly = df.groupby("month").agg({
                "liked_count": "sum",
                "collected_count": "sum",
                "comment_count": "sum",
                "note_id": "count",
            }).rename(columns={"note_id": "note_count"}).reset_index()
            monthly = monthly.sort_values("month")
            monthly_trend = monthly.to_dict("records")
        else:
            monthly_trend = []

        # 7. Day of week distribution
        if not valid_dates.empty:
            df["weekday"] = df["date"].dt.dayofweek
            weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            weekday_dist = df["weekday"].value_counts().sort_index()
            weekday_data = [
                {"day": weekday_names[int(i)], "count": int(c)}
                for i, c in weekday_dist.items()
            ]
        else:
            weekday_data = []

        # 8. Hour distribution
        if not valid_dates.empty:
            df["hour"] = df["date"].dt.hour
            hour_dist = df["hour"].value_counts().sort_index()
            hour_data = [
                {"hour": int(h), "count": int(c)}
                for h, c in hour_dist.items()
            ]
        else:
            hour_data = []

        # 9. Tag frequency
        all_tags = []
        for tags in df["tag_list"]:
            all_tags.extend(tags)
        tag_counter = {}
        for t in all_tags:
            tag_counter[t] = tag_counter.get(t, 0) + 1
        top_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)[:30]
        tag_data = [{"tag": t, "count": c} for t, c in top_tags]

        # 10. Engagement rate ranking
        df["total_engagement"] = df["liked_count"] + df["collected_count"] + df["comment_count"]
        top_engagement = df.nlargest(10, "total_engagement")[["title", "total_engagement", "note_id"]].to_dict("records")

        return {
            "summary": summary,
            "top_likes": top_likes,
            "top_collects": top_collects,
            "top_comments": top_comments,
            "top_engagement": top_engagement,
            "content_type": content_type,
            "monthly_trend": monthly_trend,
            "weekday_distribution": weekday_data,
            "hour_distribution": hour_data,
            "top_tags": tag_data,
        }


# ============================================================
# ZIP Exporter
# ============================================================

class ZIPExporter:
    """Export notes data as ZIP files."""

    def __init__(self, client: XHSClient):
        self.client = client

    async def export_note(self, note: dict, comments: list = None) -> BytesIO:
        """Export a single note as ZIP. Handles both noteCard (camelCase) and detail (snake_case) formats."""
        buf = BytesIO()
        # Support both noteCard format (noteId, displayTitle) and detail format (note_id, display_title)
        note_id = note.get("note_id") or note.get("noteId") or note.get("id") or "unknown"
        title = note.get("display_title") or note.get("displayTitle") or note.get("title") or "untitled"
        desc = note.get("desc") or note.get("displayTitle") or ""
        note_type = note.get("type", "normal")
        note_time = note.get("time") or note.get("timestamp") or 0

        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:50]

        # Extract interact info (noteCard uses interactInfo, detail uses interact_info)
        interact_info = note.get("interact_info") or note.get("interactInfo") or {}
        if not isinstance(interact_info, dict):
            interact_info = {}

        # Extract user info (noteCard uses userId/nickname, detail uses user_id/nickname)
        user_obj = note.get("user", {})
        if not isinstance(user_obj, dict):
            user_obj = {}
        user_id = user_obj.get("user_id") or user_obj.get("userId") or ""
        user_nickname = user_obj.get("nickname") or user_obj.get("nickName") or "N/A"

        # Extract image list (noteCard uses imageList, detail uses image_list)
        image_list = note.get("image_list") or note.get("imageList") or []
        if not isinstance(image_list, list):
            image_list = []

        # Extract tag list
        tag_list = note.get("tag_list") or note.get("tagList") or []
        if not isinstance(tag_list, list):
            tag_list = []

        # Extract video info
        video = note.get("video") or {}

        # Safe time formatting
        time_str = ""
        if note_time:
            try:
                time_str = datetime.fromtimestamp(int(note_time) / 1000).strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, OSError, TypeError):
                time_str = str(note_time)

        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 1. Note metadata (JSON)
            meta = {
                "note_id": note_id,
                "title": title,
                "desc": desc,
                "type": note_type,
                "time": note_time,
                "time_str": time_str,
                "interact_info": interact_info,
                "tag_list": tag_list,
                "user": {
                    "user_id": user_id,
                    "nickname": user_nickname,
                },
            }
            zf.writestr(f"{safe_title}/note_info.json", json.dumps(meta, ensure_ascii=False, indent=2, default=str))

            # 2. Note content (Markdown)
            md_content = f"# {title}\n\n"
            md_content += f"**作者**: {user_nickname}\n\n"
            md_content += f"**发布时间**: {time_str or '未知'}\n\n"
            md_content += f"**类型**: {'视频' if note_type == 'video' else '图文'}\n\n"
            liked = interact_info.get('likedCount', interact_info.get('liked_count', '0'))
            collected = interact_info.get('collectedCount', interact_info.get('collected_count', ''))
            comment = interact_info.get('commentCount', interact_info.get('comment_count', ''))
            md_content += f"**点赞**: {liked or '未知'} | "
            md_content += f"**收藏**: {collected or '未知'} | "
            md_content += f"**评论**: {comment or '未知'}\n\n---\n\n"
            if desc:
                md_content += desc
            else:
                md_content += "*（正文内容未能获取，该笔记可能限制了网页端访问）*\n"
            if tag_list:
                md_content += "\n\n**标签**: " + " ".join(
                    f"#{t.get('name', t) if isinstance(t, dict) else t}" for t in tag_list
                )
            zf.writestr(f"{safe_title}/content.md", md_content)

            # 3. Images — from imageList (detail) or cover.infoList (SSR)
            for idx, img in enumerate(image_list):
                if not isinstance(img, dict):
                    continue
                img_url = img.get("url_default") or img.get("url") or img.get("urlDefault") or ""
                if img_url and not img_url.startswith("data:"):
                    try:
                        # Remove backtick prefix if present
                        if img_url.startswith("`"):
                            img_url = img_url[1:]
                        if not img_url.startswith("http"):
                            img_url = "https:" + img_url
                        img_data = await self.client.download_file(img_url)
                        ext = self._guess_ext(img_url, img_data)
                        zf.writestr(f"{safe_title}/images/image_{idx + 1}{ext}", img_data)
                    except Exception as e:
                        print(f"[Export] Failed to download image {idx}: {e}")

            # 3b. If no imageList, try downloading cover images from cover.infoList
            if not image_list:
                cover_obj = note.get("cover", {})
                if isinstance(cover_obj, dict):
                    info_list = cover_obj.get("infoList", [])
                    if isinstance(info_list, list):
                        for idx, img_info in enumerate(info_list):
                            if not isinstance(img_info, dict):
                                continue
                            img_url = img_info.get("url", "")
                            if img_url:
                                try:
                                    if img_url.startswith("`"):
                                        img_url = img_url[1:]
                                    if not img_url.startswith("http"):
                                        img_url = "https:" + img_url
                                    img_data = await self.client.download_file(img_url)
                                    ext = self._guess_ext(img_url, img_data)
                                    zf.writestr(f"{safe_title}/images/cover_{idx + 1}{ext}", img_data)
                                except Exception as e:
                                    print(f"[Export] Failed to download cover image {idx}: {e}")

            # 4. Video
            if isinstance(video, dict) and video:
                video_key = video.get("origin_video_key", "")
                if video_key:
                    video_url = f"http://sns-video-bd.xhscdn.com/{video_key}"
                    try:
                        video_data = await self.client.download_file(video_url)
                        zf.writestr(f"{safe_title}/video.mp4", video_data)
                    except Exception as e:
                        print(f"[Export] Failed to download video: {e}")
                # Try consumer origin URL
                consumer_url = video.get("consumer", {}).get("origin_video_key", "")
                if consumer_url and not video_key:
                    try:
                        video_data = await self.client.download_file(consumer_url)
                        zf.writestr(f"{safe_title}/video.mp4", video_data)
                    except Exception as e:
                        print(f"[Export] Failed to download video (consumer): {e}")

            # 5. Comments
            if comments:
                zf.writestr(
                    f"{safe_title}/comments.json",
                    json.dumps(comments, ensure_ascii=False, indent=2, default=str),
                )
                # Also export as readable text
                comment_text = self._format_comments(comments)
                zf.writestr(f"{safe_title}/comments.txt", comment_text)

        buf.seek(0)
        return buf

    async def export_all(self, notes: list, comments_map: dict = None) -> BytesIO:
        """Export all notes as a single ZIP. Handles both noteCard (camelCase) and detail (snake_case) formats."""
        buf = BytesIO()

        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Summary file
            summary = {
                "total_notes": len(notes),
                "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "notes": [
                    {
                        "note_id": n.get("note_id") or n.get("noteId") or n.get("id") or "",
                        "title": n.get("display_title") or n.get("displayTitle") or n.get("title") or "",
                        "time": n.get("time") or n.get("timestamp") or 0,
                        "interact_info": n.get("interact_info") or n.get("interactInfo") or {},
                    }
                    for n in notes
                ],
            }
            zf.writestr("_summary.json", json.dumps(summary, ensure_ascii=False, indent=2, default=str))

            for note in notes:
                note_id = note.get("note_id") or note.get("noteId") or note.get("id") or "unknown"
                title = note.get("display_title") or note.get("displayTitle") or note.get("title") or "untitled"
                desc = note.get("desc") or ""
                note_type = note.get("type", "normal")
                note_time = note.get("time") or note.get("timestamp") or 0
                interact_info = note.get("interact_info") or note.get("interactInfo") or {}
                if not isinstance(interact_info, dict):
                    interact_info = {}
                tag_list = note.get("tag_list") or note.get("tagList") or []
                if not isinstance(tag_list, list):
                    tag_list = []
                image_list = note.get("image_list") or note.get("imageList") or []
                if not isinstance(image_list, list):
                    image_list = []

                safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:50]
                comments = comments_map.get(note_id, []) if comments_map else []

                # Safe time formatting
                time_str = ""
                if note_time:
                    try:
                        time_str = datetime.fromtimestamp(int(note_time) / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, OSError, TypeError):
                        time_str = str(note_time)

                # Note info
                meta = {
                    "note_id": note_id,
                    "title": title,
                    "desc": desc,
                    "type": note_type,
                    "time": note_time,
                    "time_str": time_str,
                    "interact_info": interact_info,
                    "tag_list": tag_list,
                }
                zf.writestr(f"{safe_title}/note_info.json", json.dumps(meta, ensure_ascii=False, indent=2, default=str))

                # Content markdown
                md = f"# {title}\n\n{desc}\n"
                zf.writestr(f"{safe_title}/content.md", md)

                # Images
                for idx, img in enumerate(image_list):
                    if not isinstance(img, dict):
                        continue
                    img_url = img.get("url_default") or img.get("url") or img.get("urlDefault") or ""
                    if img_url and not img_url.startswith("data:"):
                        try:
                            if img_url.startswith("`"):
                                img_url = img_url[1:]
                            if not img_url.startswith("http"):
                                img_url = "https:" + img_url
                            img_data = await self.client.download_file(img_url)
                            ext = self._guess_ext(img_url, img_data)
                            zf.writestr(f"{safe_title}/images/image_{idx + 1}{ext}", img_data)
                        except Exception as e:
                            print(f"[Export] Image download failed: {e}")

                # Video
                video = note.get("video") or {}
                if isinstance(video, dict) and video:
                    video_key = video.get("origin_video_key", "")
                    if video_key:
                        try:
                            video_data = await self.client.download_file(f"http://sns-video-bd.xhscdn.com/{video_key}")
                            zf.writestr(f"{safe_title}/video.mp4", video_data)
                        except Exception as e:
                            print(f"[Export] Video download failed: {e}")

                # Comments
                if comments:
                    zf.writestr(f"{safe_title}/comments.json", json.dumps(comments, ensure_ascii=False, indent=2, default=str))

        buf.seek(0)
        return buf

    @staticmethod
    def _guess_ext(url: str, data: bytes) -> str:
        if "png" in url:
            return ".png"
        if "gif" in url:
            return ".gif"
        if "webp" in url:
            return ".webp"
        if data[:4] == b'\x89PNG':
            return ".png"
        if data[:3] == b'GIF':
            return ".gif"
        if data[:4] == b'RIFF':
            return ".webp"
        return ".jpg"

    @staticmethod
    def _format_comments(comments: list, indent: int = 0) -> str:
        lines = []
        prefix = "  " * indent
        for c in comments:
            user = c.get("user", "Anonymous")
            content = c.get("content", "")
            like_count = c.get("like_count", 0)
            ip_location = c.get("ip_location", "")
            create_time = c.get("create_time", "")

            # Main comment
            time_str = f" | 🕐 {create_time}" if create_time else ""
            location_str = f" | 📍 {ip_location}" if ip_location else ""
            lines.append(f"{prefix}👤 **{user}**{time_str}{location_str}")
            lines.append(f"{prefix}   {content}")
            if like_count:
                lines.append(f"{prefix}   ❤️ {like_count}")
            lines.append("")

            # Sub-comments / replies
            sub_comments = c.get("sub_comments", [])
            if sub_comments:
                for sub in sub_comments:
                    sub_user = sub.get("user", "Anonymous")
                    sub_content = sub.get("content", "")
                    sub_like = sub.get("like_count", 0)
                    sub_time = sub.get("create_time", "")
                    target_user = sub.get("target_user", "")

                    # Build reply line
                    if target_user and target_user != sub_user:
                        reply_prefix = f"└─ **{sub_user}** 回复 **{target_user}**"
                    else:
                        reply_prefix = f"└─ **{sub_user}**"
                    sub_time_str = f" | 🕐 {sub_time}" if sub_time else ""
                    lines.append(f"{prefix}  {reply_prefix}{sub_time_str}")
                    lines.append(f"{prefix}     {sub_content}")
                    if sub_like:
                        lines.append(f"{prefix}     ❤️ {sub_like}")
                    lines.append("")
        return "\n".join(lines)


# ============================================================
# In-memory data store
# ============================================================

class DataStore:
    """In-memory store for scraped data."""

    def __init__(self):
        self.notes: list = []
        self.comments_map: dict = {}  # note_id -> comments list
        self.user_info: dict = {}
        self.search_user_id: str = ""

    def clear(self):
        self.notes = []
        self.comments_map = {}
        self.user_info = {}
        self.search_user_id = ""

    def set_notes(self, notes: list, user_id: str):
        self.notes = notes
        self.search_user_id = user_id

    def set_comments(self, note_id: str, comments: list):
        self.comments_map[note_id] = comments

    def get_note_by_id(self, note_id: str) -> Optional[dict]:
        for n in self.notes:
            nid = n.get("note_id") or n.get("noteId") or n.get("id") or ""
            if nid == note_id:
                return n
        return None


# ============================================================
# FastAPI Application
# ============================================================

# Initialize components
session_mgr = SessionManager()
browser_client = BrowserClient()
xhs_client = XHSClient(session_mgr, browser_client)
exporter = ZIPExporter(xhs_client)
store = DataStore()

app = FastAPI(title="XHS Data Scraper", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models ---

class CookieInput(BaseModel):
    cookie_str: str

class PasswordLoginInput(BaseModel):
    phone: str
    password: str

class SearchInput(BaseModel):
    user_id: str


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML page."""
    html_path = BASE_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>index.html not found. Please ensure index.html is in the same directory as server.py</h1>")


@app.get("/api/session/status")
async def get_session_status():
    """Check current login session status."""
    return {
        "logged_in": session_mgr.is_logged_in,
        "has_a1": bool(session_mgr.a1),
        "has_web_session": bool(session_mgr.cookies.get("web_session")),
        "cookie_count": len(session_mgr.cookies),
        "browser_ready": browser_client._ready,
        "cookie_keys": list(session_mgr.cookies.keys()),
    }


@app.post("/api/session/set")
async def set_session(data: CookieInput):
    """Set cookies from browser cookie string."""
    session_mgr.set_cookies(data.cookie_str)
    # Also update browser cookies
    await browser_client.update_cookies(session_mgr.cookies)
    return {
        "status": "ok",
        "logged_in": session_mgr.is_logged_in,
        "has_a1": bool(session_mgr.a1),
        "cookie_count": len(session_mgr.cookies),
    }


@app.post("/api/login/password")
async def login_password(data: PasswordLoginInput):
    """Login with phone number and password."""
    try:
        # Use browser to perform login
        await browser_client.init()
        page = browser_client._page

        # Navigate to login page
        await page.goto(f"{XHS_WEB}/login", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # Try to fill phone and password
        phone_input = await page.query_selector('input[placeholder*="手机号"]')
        pwd_input = await page.query_selector('input[type="password"]')

        if phone_input and pwd_input:
            await phone_input.fill(data.phone)
            await pwd_input.fill(data.password)
            # Click login button
            login_btn = await page.query_selector('button:has-text("登录")')
            if login_btn:
                await login_btn.click()
                await page.wait_for_timeout(5000)

                # Check if login succeeded by reading cookies
                cookies = await browser_client.get_page_cookies()
                if cookies.get("web_session"):
                    session_mgr.cookies.update(cookies)
                    session_mgr.save()
                    return {"status": "ok", "message": "登录成功", "logged_in": True}

        return {"status": "error", "message": "登录失败，请尝试扫码登录"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- QR Code Login ---

# In-memory QR login state
_qr_login_state = {}


@app.get("/api/login/qr")
async def create_qr_code():
    """Create a QR code for login using browser."""
    try:
        await browser_client.init()
        page = browser_client._page

        # Navigate to login page
        await page.goto(f"{XHS_WEB}/login", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # Find QR code element
        qr_img = await page.query_selector('img[alt*="二维码"], .qrcode img, .login-qrcode img, canvas')
        if qr_img:
            qr_src = await qr_img.get_attribute("src")
            if qr_src and qr_src.startswith("data:image"):
                # Generate a unique ID for this QR session
                qr_id = f"qr_{int(time.time() * 1000)}"
                _qr_login_state[qr_id] = {
                    "qr_id": qr_id,
                    "qr_image": qr_src,
                    "created_at": time.time(),
                    "page": page,
                }
                return {
                    "status": "ok",
                    "qr_id": qr_id,
                    "qr_image": qr_src,
                }

        # Fallback: use httpx to create QR (browser API call may not work)
        uri = "/api/sns/web/v1/login/qrcode/create"
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "User-Agent": session_mgr.user_agent,
                "Referer": XHS_WEB + "/",
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": XHS_WEB,
            }
            if session_mgr.cookies:
                headers["Cookie"] = session_mgr.get_cookie_header()
            resp = await client.post(f"{XHS_API}{uri}", json={"qr_type": 1}, headers=headers)
            data = resp.json()

        if isinstance(data, dict) and (data.get("success") or data.get("code") == 0):
            result_data = data.get("data", {})
            qr_id = result_data.get("qr_id", "")
            qr_code = result_data.get("code", "")
            qr_url = result_data.get("url", "")

            if qr_id and qr_code:
                _qr_login_state[qr_id] = {
                    "qr_id": qr_id,
                    "code": qr_code,
                    "url": qr_url,
                    "created_at": time.time(),
                }
                return {
                    "status": "ok",
                    "qr_id": qr_id,
                    "code": qr_code,
                    "qr_url": qr_url,
                }

        return {"status": "error", "message": "无法获取二维码，请刷新重试"}
    except Exception as e:
        print(f"[QRLogin] Create QR error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/login/qr/status")
async def check_qr_status(qr_id: str = Query(...), code: str = Query("")):
    """Check QR code scan status."""
    if qr_id not in _qr_login_state:
        return {"status": "error", "message": "Invalid or expired QR session"}

    state = _qr_login_state[qr_id]

    # Check expiration (5 minutes)
    if time.time() - state["created_at"] > 300:
        _qr_login_state.pop(qr_id, None)
        return {"status": "expired", "message": "QR code expired"}

    try:
        # Check if browser has obtained login cookies
        cookies = await browser_client.get_page_cookies()
        if cookies.get("web_session"):
            session_mgr.cookies.update(cookies)
            session_mgr.save()
            _qr_login_state.pop(qr_id, None)
            print(f"[QRLogin] Login success via browser! cookies: {list(cookies.keys())}")
            return {
                "status": "success",
                "message": "登录成功",
                "logged_in": True,
                "cookie_count": len(session_mgr.cookies),
            }

        # Fallback: poll API if we have code
        if state.get("code"):
            uri = "/api/sns/web/v1/login/qrcode/status"
            params = {
                "qr_id": state["qr_id"],
                "code": state["code"],
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "User-Agent": session_mgr.user_agent,
                    "Referer": XHS_WEB + "/",
                    "Origin": XHS_WEB,
                }
                if session_mgr.cookies:
                    headers["Cookie"] = session_mgr.get_cookie_header()
                resp = await client.get(f"{XHS_API}{uri}", params=params, headers=headers)
                data = resp.json()

            if isinstance(data, dict):
                result_data = data.get("data", {})
                code_status = result_data.get("code_status", -1)

                if code_status == 1:
                    return {"status": "scanned", "message": "已扫码，请在手机上确认登录"}
                elif code_status == 2:
                    login_info = result_data.get("login_info", {})
                    new_session = login_info.get("session", "") or login_info.get("secure_session", "")

                    if new_session:
                        session_mgr.cookies["web_session"] = new_session
                        session_mgr.save()
                        await browser_client.update_cookies(session_mgr.cookies)

                    _qr_login_state.pop(qr_id, None)
                    return {
                        "status": "success",
                        "message": "登录成功",
                        "logged_in": session_mgr.is_logged_in,
                    }
                elif code_status == 3:
                    _qr_login_state.pop(qr_id, None)
                    return {"status": "expired", "message": "二维码已过期，请刷新"}

        return {"status": "waiting", "message": "等待扫码..."}
    except Exception as e:
        print(f"[QRLogin] Check status error: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/search")
async def search_notes(data: SearchInput):
    """Search all notes by author ID."""
    user_id = data.user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    # Ensure browser is ready
    if not browser_client._ready:
        ok = await browser_client.init()
        if not ok:
            raise HTTPException(
                status_code=503,
                detail=f"浏览器服务未就绪: {browser_client._init_error}。请确保已安装 Playwright: pip install playwright && playwright install chromium"
            )

    try:
        # Fetch user info (non-critical, continue even if it fails)
        user_info = {}
        try:
            user_info = await xhs_client.get_user_info(user_id)
            store.user_info = user_info
        except Exception as e:
            print(f"[Search] get_user_info failed (non-critical): {e}")

        # Fetch all notes
        notes = await xhs_client.get_user_notes(user_id)
        if not notes:
            return {"notes": [], "user_info": user_info, "total": 0}

        store.set_notes(notes, user_id)

        # Enrich notes with detail data (desc, time, imageList, full interactInfo)
        # SSR list only has: noteId, displayTitle, type, user, interactInfo(likedCount only), cover
        # Detail page has: desc, time, imageList, video, full interactInfo, tagList
        print(f"[Search] Enriching {len(notes)} notes with detail data...")
        enriched_count = 0
        for idx, n in enumerate(notes):
            note_id = n.get("noteId") or n.get("id") or ""
            if not note_id:
                continue
            # Skip if already has desc (from previous enrichment or detail fetch)
            if n.get("desc"):
                continue
            try:
                xsec_token = n.get("xsecToken", "")
                detail = await xhs_client.get_note_detail(note_id, xsec_token=xsec_token)
                if detail and isinstance(detail, dict):
                    # Merge detail data into noteCard (detail fields take priority)
                    if detail.get("desc"):
                        n["desc"] = detail["desc"]
                    if detail.get("time") or detail.get("timestamp"):
                        n["time"] = detail.get("time") or detail.get("timestamp")
                    if detail.get("imageList"):
                        n["imageList"] = detail["imageList"]
                    if detail.get("video"):
                        n["video"] = detail["video"]
                    if detail.get("tagList"):
                        n["tagList"] = detail["tagList"]
                    # Merge interactInfo
                    detail_interact = detail.get("interactInfo") or detail.get("interact_info") or {}
                    if isinstance(detail_interact, dict):
                        existing_interact = n.get("interactInfo", {})
                        if isinstance(existing_interact, dict):
                            merged = {**existing_interact}
                            for k in ["collectedCount", "commentCount", "shareCount", "collected_count", "comment_count", "share_count"]:
                                if detail_interact.get(k):
                                    merged[k] = detail_interact[k]
                            n["interactInfo"] = merged
                    enriched_count += 1
                    if enriched_count <= 3:
                        print(f"[Search] Enriched note {note_id[:12]}: desc={'yes' if n.get('desc') else 'no'}, time={'yes' if n.get('time') else 'no'}, images={len(n.get('imageList', []))}")
                    # Small delay to avoid triggering anti-crawl
                    await asyncio.sleep(1.5)
            except Exception as e:
                print(f"[Search] Detail fetch failed for {note_id[:12]}: {e}")
                # If we get consecutive failures, stop trying (likely blocked)
                if idx > 2 and enriched_count == 0:
                    print(f"[Search] Too many consecutive failures, stopping enrichment")
                    break
                await asyncio.sleep(2)
        print(f"[Search] Enriched {enriched_count}/{len(notes)} notes with detail data")

        # Update store with enriched notes
        store.set_notes(notes, user_id)

        # Format notes for frontend
        formatted = []
        for idx, n in enumerate(notes):
            try:
                # Debug: print first note's actual keys to understand SSR structure
                if idx == 0:
                    print(f"[Client] First note keys: {list(n.keys())[:20]}")
                    print(f"[Client] First note sample: {json.dumps(n, ensure_ascii=False, default=str)[:500]}")

                # noteCard actual structure:
                # {noteId, xsecToken, type, displayTitle, user: {nickname, userId, avatar},
                #  interactInfo: {liked, likedCount, collected, collectedCount, ...},
                #  cover: {url, width, height, infoList: [{imageScene, url}]}
                #  imageList may exist for multi-image notes, video for video notes}
                interact = n.get("interactInfo", {})
                if not isinstance(interact, dict):
                    interact = {}
                note_id = n.get("noteId", n.get("id", ""))
                title = n.get("displayTitle", "")
                desc = n.get("desc", "")
                note_type = n.get("type", "normal")
                note_time = n.get("time", n.get("timestamp", 0))
                video = n.get("video", {})

                # Author info
                author_name = ""
                user_obj = n.get("user", {})
                if isinstance(user_obj, dict):
                    author_name = user_obj.get("nickname", user_obj.get("nickName", ""))

                # Cover image — from cover.infoList or cover.url
                cover_url = ""
                cover_obj = n.get("cover", {})
                if isinstance(cover_obj, dict):
                    info_list = cover_obj.get("infoList", [])
                    if isinstance(info_list, list) and info_list:
                        for img_info in info_list:
                            if isinstance(img_info, dict):
                                url = img_info.get("url", "")
                                if url:
                                    # Remove backtick prefix if present
                                    if url.startswith("`"):
                                        url = url[1:]
                                    if url.startswith("//"):
                                        url = "https:" + url
                                    elif not url.startswith("http"):
                                        url = "https:" + url
                                    cover_url = url
                                    break
                    if not cover_url:
                        url = cover_obj.get("url", "")
                        if url:
                            if url.startswith("`"):
                                url = url[1:]
                            if url.startswith("//"):
                                url = "https:" + url
                            elif not url.startswith("http"):
                                url = "https:" + url
                            cover_url = url

                # Image count
                image_list = n.get("imageList", [])
                image_count = len(image_list) if isinstance(image_list, list) else 0

                # Interact counts — SSR may only have likedCount, default others to "0"
                liked_count = str(interact.get("likedCount", "0"))
                collected_count = str(interact.get("collectedCount", "0"))
                comment_count = str(interact.get("commentCount", "0"))
                share_count = str(interact.get("shareCount", "0"))

                # Safe time formatting
                time_str = "N/A"
                if note_time:
                    try:
                        time_str = datetime.fromtimestamp(int(note_time) / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, OSError, TypeError):
                        time_str = str(note_time)

                formatted.append({
                    "note_id": note_id,
                    "title": title,
                    "desc": desc[:200] if desc else "",
                    "type": note_type,
                    "time": note_time,
                    "time_str": time_str,
                    "liked_count": liked_count,
                    "collected_count": collected_count,
                    "comment_count": comment_count,
                    "share_count": share_count,
                    "cover_url": cover_url,
                    "image_count": image_count,
                    "has_video": bool(video),
                    "author": author_name,
                    "note_url": f"https://www.xiaohongshu.com/explore/{note_id}" + (f"?xsec_token={n.get('xsecToken', '')}&xsec_source=pc_user" if n.get('xsecToken') else ""),
                })
            except Exception as e:
                print(f"[Search] Error formatting note #{idx}: {e}")
                traceback.print_exc()
                continue

        # Safely extract user_info fields — interactions may be a list, not dict
        basic_info = user_info.get("basicInfo", {})
        if not isinstance(basic_info, dict):
            basic_info = {}
        interactions = user_info.get("interactions", [])
        # interactions can be list or dict; extract counts safely
        fans = "0"
        follows = "0"
        interaction_total = "0"
        if isinstance(interactions, dict):
            fans = str(interactions.get("fansCount", "0"))
            follows = str(interactions.get("followsCount", "0"))
            interaction_total = str(interactions.get("interactionCount", "0"))
        elif isinstance(interactions, list) and interactions:
            # List format: try to find fans/follows in first item or by key matching
            for item in interactions:
                if isinstance(item, dict):
                    fans = str(item.get("fansCount", item.get("fans", "0")))
                    follows = str(item.get("followsCount", item.get("follows", "0")))
                    interaction_total = str(item.get("interactionCount", item.get("interaction", "0")))
                    break

        return {
            "notes": formatted,
            "user_info": {
                "nickname": basic_info.get("nickname", ""),
                "user_id": user_id,
                "desc": basic_info.get("desc", ""),
                "fans": fans,
                "follows": follows,
                "interaction": interaction_total,
            },
            "total": len(formatted),
            "enriched": enriched_count,
            "data_warning": "" if enriched_count == len(notes) else
                f"部分笔记详情无法获取（{len(notes) - enriched_count}/{len(notes)}），收藏数、评论数、正文内容可能不完整。这可能是因为笔记限制了网页端访问。" if enriched_count > 0 else
                f"所有笔记详情均无法获取，收藏数、评论数、正文内容不可用。该作者的笔记可能限制了网页端浏览。",
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.get("/api/note/{note_id}")
async def get_note_detail(note_id: str):
    """Get detailed info for a specific note."""
    detail = await xhs_client.get_note_detail(note_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Note not found")
    return detail


@app.get("/api/note/{note_id}/comments")
async def get_note_comments(note_id: str):
    """Get all comments for a specific note."""
    # Check cache first
    if note_id in store.comments_map:
        return {"comments": store.comments_map[note_id], "cached": True}

    # Try to get xsec_token from store
    xsec_token = ""
    note_in_store = store.get_note_by_id(note_id)
    if note_in_store:
        xsec_token = note_in_store.get("xsecToken", "")

    comments = await xhs_client.get_note_comments(note_id, xsec_token=xsec_token)
    store.set_comments(note_id, comments)
    return {"comments": comments, "cached": False}


@app.post("/api/download/{note_id}")
async def download_note(note_id: str):
    """Download a single note as ZIP (with comments)."""
    note = store.get_note_by_id(note_id)
    xsec_token = ""
    if note:
        xsec_token = note.get("xsecToken", "")
    if not note:
        # Note not in store — try fetching detail page (may fail if note is restricted)
        try:
            note = await xhs_client.get_note_detail(note_id)
        except Exception as e:
            print(f"[Download] Failed to fetch note detail for {note_id}: {e}")
    if not note:
        raise HTTPException(status_code=404, detail="笔记未找到或无法访问。该笔记可能已被删除或限制浏览。")

    # Fetch comments if not cached (non-critical — skip if fails)
    if note_id not in store.comments_map:
        try:
            comments = await xhs_client.get_note_comments(note_id, xsec_token=xsec_token)
            store.set_comments(note_id, comments)
        except Exception as e:
            print(f"[Download] Failed to fetch comments for {note_id}: {e}")
            store.set_comments(note_id, [])

    comments = store.comments_map.get(note_id, [])
    zip_buf = await exporter.export_note(note, comments)

    title = note.get("display_title", note.get("displayTitle", note.get("title", "note")))
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:30]
    filename = f"{safe_title}_{note_id[:8]}.zip"
    encoded_filename = quote(filename)

    return StreamingResponse(
        BytesIO(zip_buf.getvalue()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


@app.post("/api/download_all")
async def download_all_notes():
    """Download all searched notes as a single ZIP."""
    if not store.notes:
        raise HTTPException(status_code=400, detail="No notes to download. Please search first.")

    # Fetch comments for all notes (with caching)
    for note in store.notes:
        note_id = note.get("note_id") or note.get("noteId") or note.get("id") or ""
        xsec_token = note.get("xsecToken", "")
        if note_id and note_id not in store.comments_map:
            try:
                comments = await xhs_client.get_note_comments(note_id, xsec_token=xsec_token)
                store.set_comments(note_id, comments)
            except Exception as e:
                print(f"[DownloadAll] Failed to fetch comments for {note_id}: {e}")

    zip_buf = await exporter.export_all(store.notes, store.comments_map)

    user_nickname = store.user_info.get("user", {}).get("nickname", "user")
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', user_nickname)[:20]
    filename = f"xhs_{safe_name}_all_notes.zip"
    encoded_filename = quote(filename)

    return StreamingResponse(
        BytesIO(zip_buf.getvalue()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


@app.post("/api/analyze")
async def analyze_data():
    """Analyze all searched notes data."""
    if not store.notes:
        raise HTTPException(status_code=400, detail="No notes to analyze. Please search first.")

    analyzer = DataAnalyzer(store.notes)
    result = analyzer.analyze()
    return result


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "browser_ready": browser_client._ready,
        "logged_in": session_mgr.is_logged_in,
    }


# --- Startup/Shutdown ---

@app.on_event("shutdown")
async def shutdown():
    await xhs_client.close()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  XHS Data Scraper - Proxy Server v2.0")
    print("  (Browser-assisted signing via Playwright)")
    print(f"  Access: http://localhost:{PORT}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
