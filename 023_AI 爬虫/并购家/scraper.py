"""
ipoipo.cn 行业报告爬虫模块
爬取近N天的报告标题、链接、日期和真实zip下载地址

优化策略：浏览器仅启动一次通过反爬验证获取 Cookie，
之后全部使用 requests + Cookie 高速请求（毫秒级）。
"""

import re
import time
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class IPOScraper:
    BASE_URL = 'https://ipoipo.cn'
    MAX_RETRIES = 3
    REQUEST_DELAY = 0.3  # requests 请求间隔（秒）—— 有 Cookie 后可以很短
    BROWSER_WAIT = 8     # 等待 JS 反爬执行完毕（秒）
    PAGE_LOAD_TIMEOUT = 30  # 页面加载超时（秒）
    MAX_WORKERS = 5       # 并发下载页线程数

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self._default_headers())
        self._browser = None
        self._browser_type = None
        self._browser_initialized = False
        self._cookie_verified = False  # Cookie 是否已通过反爬验证

    def _default_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://ipoipo.cn/',
        }

    # ==================== 浏览器（仅用于过反爬拿 Cookie） ====================

    def _init_browser(self):
        """延迟初始化浏览器"""
        if self._browser_initialized:
            return
        if not self._try_init_drissionpage():
            if not self._try_init_selenium():
                logger.error('所有浏览器方案均启动失败')
                self._browser_initialized = False

    def _try_init_drissionpage(self):
        try:
            from DrissionPage import ChromiumPage, ChromiumOptions
            co = ChromiumOptions()
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-gpu')
            co.set_argument('--headless=new')
            co.set_argument('--disable-dev-shm-usage')
            co.auto_port()
            browser_path = self._find_browser_path()
            if browser_path:
                co.set_browser_path(browser_path)
                logger.info(f'[DrissionPage] 使用浏览器: {browser_path}')
            self._browser = ChromiumPage(co)
            self._browser_type = 'drissionpage'
            self._browser_initialized = True
            logger.info('浏览器已启动（DrissionPage headless 模式）')
            return True
        except Exception as e:
            logger.warning(f'[DrissionPage] 启动失败: {e}')
            return False

    def _try_init_selenium(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from selenium.webdriver.chrome.options import Options as ChromeOptions

            browser_path = self._find_browser_path()
            browser_name = ''
            common_args = [
                '--headless=new', '--no-sandbox', '--disable-gpu',
                '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled',
                '--disable-extensions', '--disable-infobars',
                '--window-size=1920,1080', '--lang=zh-CN',
            ]

            def _make_opts(cls):
                opts = cls()
                for arg in common_args:
                    opts.add_argument(arg)
                opts.add_experimental_option('excludeSwitches', ['enable-automation'])
                opts.add_experimental_option('useAutomationExtension', False)
                return opts

            if browser_path and 'msedge' in browser_path.lower():
                opts = _make_opts(EdgeOptions)
                opts.binary_location = browser_path
                browser_name = 'Edge'
                self._browser = webdriver.Edge(options=opts)
            elif browser_path and 'chrome' in browser_path.lower():
                opts = _make_opts(ChromeOptions)
                opts.binary_location = browser_path
                browser_name = 'Chrome'
                self._browser = webdriver.Chrome(options=opts)
            else:
                try:
                    self._browser = webdriver.Edge(options=_make_opts(EdgeOptions))
                    browser_name = 'Edge'
                except Exception:
                    self._browser = webdriver.Chrome(options=_make_opts(ChromeOptions))
                    browser_name = 'Chrome'

            self._browser.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
            self._browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
            self._browser_type = 'selenium'
            self._browser_initialized = True
            logger.info(f'浏览器已启动（Selenium + {browser_name} headless 模式）')
            return True
        except ImportError:
            logger.warning('[Selenium] 未安装')
            return False
        except Exception as e:
            logger.warning(f'[Selenium] 启动失败: {e}')
            return False

    def _close_browser(self):
        if self._browser:
            try:
                self._browser.quit()
            except Exception:
                pass
            self._browser = None
            self._browser_initialized = False
            self._browser_type = None

    def _browser_get(self, url):
        """用浏览器访问 URL，返回 HTML"""
        if self._browser_type == 'selenium':
            from selenium.common.exceptions import TimeoutException
            try:
                self._browser.get(url)
            except TimeoutException:
                logger.warning(f'页面加载超时（{self.PAGE_LOAD_TIMEOUT}s），继续等待JS...')
            time.sleep(self.BROWSER_WAIT)
            return self._browser.page_source
        else:
            self._browser.get(url)
            time.sleep(self.BROWSER_WAIT)
            return self._browser.html

    def _verify_cookie_with_browser(self, url):
        """
        用浏览器访问 URL，通过反爬验证，将 Cookie 注入 requests session。
        返回 (html, success)
        """
        self._init_browser()
        if not self._browser or not self._browser_initialized:
            return None, False

        for attempt in range(self.MAX_RETRIES):
            try:
                html = self._browser_get(url)
                if html and len(html) > 500 and ('wapost' in html or '/post/' in html):
                    # 成功！提取 Cookie 注入 requests
                    self._inject_cookies_from_browser()
                    self._cookie_verified = True
                    logger.info('反爬验证通过，Cookie 已注入 requests session')
                    return html, True
                logger.warning(f'浏览器获取内容疑似被拦截 (第{attempt + 1}次)，重试...')
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2)
            except Exception as e:
                logger.warning(f'浏览器请求失败 (第{attempt + 1}次): {e}')
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2)

        return None, False

    def _inject_cookies_from_browser(self):
        """从浏览器提取 Cookie 注入 requests session"""
        try:
            if self._browser_type == 'selenium':
                cookies = self._browser.get_cookies()
                for cookie in cookies:
                    self.session.cookies.set(
                        cookie['name'],
                        cookie['value'],
                        domain=cookie.get('domain', ''),
                        path=cookie.get('path', '/'),
                    )
            else:
                # DrissionPage
                for cookie in self._browser.cookies():
                    self.session.cookies.set(
                        cookie.get('name', ''),
                        cookie.get('value', ''),
                        domain=cookie.get('domain', ''),
                        path=cookie.get('path', '/'),
                    )
            logger.info(f'已注入 {len(self.session.cookies)} 个 Cookie')
        except Exception as e:
            logger.warning(f'Cookie 注入失败: {e}')

    # ==================== 高速 requests 请求 ====================

    def _fetch_fast(self, url, retries=None):
        """使用 requests + Cookie 高速获取页面（毫秒级）"""
        if retries is None:
            retries = self.MAX_RETRIES
        for attempt in range(retries):
            try:
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
                resp.encoding = resp.apparent_encoding or 'utf-8'
                html = resp.text
                # 检查是否被反爬拦截
                if html and len(html) > 500 and 'wapost' not in html and '/post/' not in html:
                    # Cookie 失效，需要重新验证
                    logger.warning('Cookie 已失效，需要重新通过反爬验证')
                    self._cookie_verified = False
                    return None  # 返回 None 让上层走浏览器验证
                return html
            except requests.RequestException as e:
                logger.warning(f'requests 请求失败 (第{attempt + 1}次): {e}')
                if attempt < retries - 1:
                    time.sleep(1)
        return None

    def _fetch(self, url):
        """
        智能获取页面：
        1. 如果 Cookie 已验证 → requests 高速请求
        2. 如果 Cookie 失效/未验证 → 浏览器过反爬 → 注入 Cookie → requests 高速请求
        """
        # 方案1: 有 Cookie，直接 requests 高速请求
        if self._cookie_verified:
            html = self._fetch_fast(url)
            if html:
                return html
            # Cookie 失效，走方案2

        # 方案2: 浏览器过反爬拿 Cookie
        logger.info(f'需要浏览器验证: {url}')
        html, success = self._verify_cookie_with_browser(url)
        if success and html:
            return html

        # 方案3: 浏览器也失败，用 requests 最后尝试（可能无反爬的页面）
        logger.warning('浏览器验证失败，回退到 requests')
        return self._fetch_fast(url)

    # ==================== 页面解析 ====================

    def _parse_list_page(self, html):
        """解析列表页"""
        soup = BeautifulSoup(html, 'lxml')
        items = []
        for article in soup.select('div.wapost.card'):
            h2 = article.select_one('h2.multi-ellipsis a')
            if not h2:
                continue
            title = h2.get_text(strip=True)
            link = h2.get('href', '')
            date_str = ''
            edit_span = article.select_one('span.edit')
            if edit_span:
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', edit_span.get_text())
                if date_match:
                    date_str = date_match.group(1)
            post_id = self._extract_id(link)
            if not post_id:
                continue
            thumbnail = ''
            img = article.select_one('p.img img')
            if img:
                thumbnail = img.get('src', '')
            views = 0
            view_span = article.select_one('span.view-num')
            if view_span:
                view_match = re.search(r'(\d+)', view_span.get_text())
                if view_match:
                    views = int(view_match.group(1))
            items.append({
                'id': post_id, 'title': title,
                'link': urljoin(self.BASE_URL, link),
                'date': date_str, 'thumbnail': thumbnail, 'views': views,
            })
        return items

    def _get_download_url(self, post_id):
        """获取真实 zip 下载地址（使用 requests 高速请求）"""
        url = f'{self.BASE_URL}/download/{post_id}.html'
        html = self._fetch_fast(url)
        if not html:
            return None
        soup = BeautifulSoup(html, 'lxml')
        zip_link = soup.find('a', href=re.compile(r'\.zip$'))
        if zip_link:
            return urljoin(self.BASE_URL, zip_link.get('href', ''))
        return None

    def _extract_id(self, url):
        match = re.search(r'post/(\d+)\.html', url)
        return match.group(1) if match else ''

    # ==================== 主流程 ====================

    def fetch_recent_reports(self, days=7, progress_callback=None):
        """爬取近N天的报告数据（优化版：浏览器只启动1次，后续全 requests）"""
        cutoff_str = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        logger.info(f'开始爬取近{days}天报告（截止日期: {cutoff_str}）')

        all_reports = []
        page = 1
        should_stop = False

        try:
            # ===== 阶段1: 浏览器获取列表页（同时过反爬拿 Cookie） =====
            while not should_stop:
                url = f'{self.BASE_URL}/category-6.html' if page == 1 \
                    else f'{self.BASE_URL}/category-6_{page}.html'

                if progress_callback:
                    progress_callback(f'正在获取第 {page} 页...')

                logger.info(f'正在爬取列表页: {url}')
                html = self._fetch(url)  # 首次会走浏览器，后续走 requests
                if not html:
                    logger.error(f'列表页获取失败: {url}')
                    break

                items = self._parse_list_page(html)
                if not items:
                    logger.info(f'第{page}页无数据，停止翻页')
                    break

                page_has_old = False
                for item in items:
                    if item['date'] and item['date'] < cutoff_str:
                        page_has_old = True
                        continue
                    all_reports.append(item)

                if page_has_old:
                    should_stop = True
                page += 1
                if not should_stop:
                    time.sleep(self.REQUEST_DELAY)

            logger.info(f'列表页解析完成，共 {len(all_reports)} 条在范围内')

            # ===== 阶段2: 并发获取下载地址（requests 高速，毫秒级） =====
            if all_reports:
                if progress_callback:
                    progress_callback(f'正在并发获取 {len(all_reports)} 个下载地址...')

                def fetch_dl(item):
                    dl_url = self._get_download_url(item['id'])
                    item['download_url'] = dl_url
                    return item

                done = 0
                with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
                    futures = {executor.submit(fetch_dl, item): item for item in all_reports}
                    for future in as_completed(futures):
                        item = future.result()
                        done += 1
                        dl = '✓' if item['download_url'] else '✗'
                        logger.info(f'  [{done}/{len(all_reports)}] {dl} [{item["date"]}] {item["title"]}')
                        if progress_callback:
                            progress_callback(f'下载地址进度: {done}/{len(all_reports)}')
                        time.sleep(self.REQUEST_DELAY)  # 礼貌间隔

        finally:
            self._close_browser()

        all_reports.sort(key=lambda x: (-self._date_to_timestamp(x['date']), x['title']))
        logger.info(f'爬取完成，共获取 {len(all_reports)} 条报告')
        return all_reports

    def _date_to_timestamp(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').timestamp()
        except (ValueError, TypeError):
            return 0

    def get_headers(self):
        return dict(self.session.headers)

    @staticmethod
    def _find_browser_path():
        import os, subprocess
        candidates = [
            os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%LocalAppData%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%ProgramFiles%\Microsoft\Edge\Application\msedge.exe'),
            os.path.expandvars(r'%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe'),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        for reg_key in [
            r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe',
            r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe',
        ]:
            try:
                result = subprocess.run(['reg', 'query', reg_key, '/ve'],
                                        capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if 'REG_SZ' in line:
                            exe_path = line.split('REG_SZ')[-1].strip()
                            if os.path.isfile(exe_path):
                                return exe_path
            except Exception:
                pass
        return None


if __name__ == '__main__':
    scraper = IPOScraper()
    def progress(msg):
        print(f'[进度] {msg}')
    t0 = time.time()
    reports = scraper.fetch_recent_reports(days=7, progress_callback=progress)
    elapsed = time.time() - t0
    print(f'\n共获取 {len(reports)} 条报告，耗时 {elapsed:.1f} 秒')
    for r in reports:
        dl = '✓' if r['download_url'] else '✗'
        print(f'  {dl} [{r["date"]}] {r["title"]}')
