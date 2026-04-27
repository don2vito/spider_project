"""
ipoipo.cn 行业报告爬虫模块
爬取近N天的报告标题、链接、日期和真实zip下载地址

注意：网站已启用 JS 反爬防护（/_guard/auto.js），
需要使用浏览器自动化绕过。优先使用 DrissionPage，失败时回退到 Selenium。
"""

import re
import time
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin

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
    REQUEST_DELAY = 1.5  # 请求间隔（秒）
    BROWSER_WAIT = 8     # 等待 JS 反爬执行完毕（秒）
    PAGE_LOAD_TIMEOUT = 30  # 页面加载超时（秒）

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self._default_headers())
        self._browser = None
        self._browser_type = None  # 'drissionpage' or 'selenium'
        self._browser_initialized = False

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

    def _init_browser(self):
        """延迟初始化浏览器，依次尝试 DrissionPage → Selenium"""
        if self._browser_initialized:
            return

        # 方案1: DrissionPage
        if not self._try_init_drissionpage():
            # 方案2: Selenium + Edge/Chrome
            if not self._try_init_selenium():
                logger.error('所有浏览器方案均启动失败')
                self._browser_initialized = False

    def _try_init_drissionpage(self):
        """尝试使用 DrissionPage 初始化浏览器"""
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
        """尝试使用 Selenium 初始化浏览器"""
        try:
            from selenium import webdriver
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from selenium.webdriver.chrome.options import Options as ChromeOptions

            browser_path = self._find_browser_path()
            browser_name = ''

            # 通用反检测参数
            common_args = [
                '--headless=new',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--disable-infobars',
                '--window-size=1920,1080',
                '--lang=zh-CN',
            ]

            if browser_path and 'msedge' in browser_path.lower():
                opts = EdgeOptions()
                for arg in common_args:
                    opts.add_argument(arg)
                opts.add_experimental_option('excludeSwitches', ['enable-automation'])
                opts.add_experimental_option('useAutomationExtension', False)
                opts.binary_location = browser_path
                browser_name = 'Edge'
                self._browser = webdriver.Edge(options=opts)
            elif browser_path and 'chrome' in browser_path.lower():
                opts = ChromeOptions()
                for arg in common_args:
                    opts.add_argument(arg)
                opts.add_experimental_option('excludeSwitches', ['enable-automation'])
                opts.add_experimental_option('useAutomationExtension', False)
                opts.binary_location = browser_path
                browser_name = 'Chrome'
                self._browser = webdriver.Chrome(options=opts)
            else:
                try:
                    opts = EdgeOptions()
                    for arg in common_args:
                        opts.add_argument(arg)
                    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
                    opts.add_experimental_option('useAutomationExtension', False)
                    self._browser = webdriver.Edge(options=opts)
                    browser_name = 'Edge'
                except Exception:
                    opts = ChromeOptions()
                    for arg in common_args:
                        opts.add_argument(arg)
                    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
                    opts.add_experimental_option('useAutomationExtension', False)
                    self._browser = webdriver.Chrome(options=opts)
                    browser_name = 'Chrome'

            # 设置页面加载超时，避免无限等待
            self._browser.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)

            # 隐藏 webdriver 特征
            self._browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })

            self._browser_type = 'selenium'
            self._browser_initialized = True
            logger.info(f'浏览器已启动（Selenium + {browser_name} headless 模式）')
            return True
        except ImportError:
            logger.warning('[Selenium] 未安装，请运行: pip install selenium')
            return False
        except Exception as e:
            logger.warning(f'[Selenium] 启动失败: {e}')
            return False

    def _close_browser(self):
        """关闭浏览器"""
        if self._browser:
            try:
                if self._browser_type == 'selenium':
                    self._browser.quit()
                else:
                    self._browser.quit()
            except Exception:
                pass
            self._browser = None
            self._browser_initialized = False
            self._browser_type = None

    def _fetch(self, url, retries=None):
        """
        获取页面 HTML（自动处理 JS 反爬）
        优先使用浏览器，失败时回退到 requests
        """
        if retries is None:
            retries = self.MAX_RETRIES

        # 尝试浏览器方式
        self._init_browser()
        if self._browser and self._browser_initialized:
            for attempt in range(retries):
                try:
                    if self._browser_type == 'selenium':
                        from selenium.common.exceptions import TimeoutException
                        try:
                            self._browser.get(url)
                        except TimeoutException:
                            logger.warning(f'页面加载超时（{self.PAGE_LOAD_TIMEOUT}s），继续等待JS执行...')
                        time.sleep(self.BROWSER_WAIT)
                        html = self._browser.page_source
                    else:
                        self._browser.get(url)
                        time.sleep(self.BROWSER_WAIT)
                        html = self._browser.html

                    # 验证是否获取到真实内容
                    if html and len(html) > 500 and ('wapost' in html or '/post/' in html):
                        return html
                    logger.warning(f'浏览器获取内容疑似被拦截 (第{attempt + 1}次)，重试...')
                    if attempt < retries - 1:
                        time.sleep(3)
                except Exception as e:
                    logger.warning(f'浏览器请求失败 (第{attempt + 1}次): {url} - {e}')
                    if attempt < retries - 1:
                        time.sleep(3)
            logger.warning('浏览器方式失败，回退到 requests')

        # 回退到 requests（适用于无反爬的下载页等）
        for attempt in range(retries):
            try:
                resp = self.session.get(url, timeout=20)
                resp.raise_for_status()
                resp.encoding = resp.apparent_encoding or 'utf-8'
                html = resp.text
                if html and len(html) > 500:
                    return html
            except requests.RequestException as e:
                logger.warning(f'requests 请求失败 (第{attempt + 1}次): {url} - {e}')
                if attempt < retries - 1:
                    time.sleep(3 * (attempt + 1))

        logger.error(f'请求最终失败: {url}')
        return None

    def _parse_list_page(self, html):
        """
        解析列表页，提取每条报告记录
        DOM结构: div.wapost.card > h2.multi-ellipsis > a (标题+链接)
                                    div.count > span.edit > i.fa-clock-o + 日期文本
        """
        soup = BeautifulSoup(html, 'lxml')
        items = []
        articles = soup.select('div.wapost.card')

        for article in articles:
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
                'id': post_id,
                'title': title,
                'link': urljoin(self.BASE_URL, link),
                'date': date_str,
                'thumbnail': thumbnail,
                'views': views,
            })

        return items

    def _get_download_url(self, post_id):
        """从下载页获取真实zip下载地址"""
        download_page_url = f'{self.BASE_URL}/download/{post_id}.html'
        html = self._fetch(download_page_url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'lxml')
        zip_link = soup.find('a', href=re.compile(r'\.zip$'))
        if zip_link:
            zip_url = zip_link.get('href', '')
            return urljoin(self.BASE_URL, zip_url)
        return None

    def _extract_id(self, url):
        """从URL中提取文章ID，如 post/26011.html -> 26011"""
        match = re.search(r'post/(\d+)\.html', url)
        return match.group(1) if match else ''

    def fetch_recent_reports(self, days=7, progress_callback=None):
        """爬取近N天的报告数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        logger.info(f'开始爬取近{days}天报告（截止日期: {cutoff_str}）')

        all_reports = []
        page = 1
        should_stop = False

        try:
            while not should_stop:
                if page == 1:
                    url = f'{self.BASE_URL}/category-6.html'
                else:
                    url = f'{self.BASE_URL}/category-6_{page}.html'

                if progress_callback:
                    progress_callback(f'正在获取第 {page} 页...')

                logger.info(f'正在爬取列表页: {url}')
                html = self._fetch(url)
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

                    if progress_callback:
                        progress_callback(f'正在获取下载地址: {item["title"][:20]}...')

                    download_url = self._get_download_url(item['id'])
                    item['download_url'] = download_url

                    if download_url:
                        logger.info(f'  ✓ [{item["date"]}] {item["title"]}')
                    else:
                        logger.warning(f'  ✗ [{item["date"]}] {item["title"]} - 未找到下载链接')

                    all_reports.append(item)
                    time.sleep(self.REQUEST_DELAY)

                if page_has_old:
                    should_stop = True

                page += 1
                if not should_stop:
                    time.sleep(self.REQUEST_DELAY)
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
        """自动检测系统中的 Chrome / Edge 浏览器路径"""
        import os
        import subprocess

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

        # 注册表查找
        for reg_key in [
            r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe',
            r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe',
        ]:
            try:
                result = subprocess.run(
                    ['reg', 'query', reg_key, '/ve'],
                    capture_output=True, text=True, timeout=5
                )
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
    reports = scraper.fetch_recent_reports(days=7, progress_callback=progress)
    print(f'\n共获取 {len(reports)} 条报告:')
    for r in reports:
        dl = '✓' if r['download_url'] else '✗'
        print(f'  {dl} [{r["date"]}] {r["title"]}')
