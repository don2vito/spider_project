"""
国家统计局 API V2.0 客户端封装
负责与 data.stats.gov.cn 新版 API 交互，处理 Cookie、速率控制、缓存等。
"""

import time
import random
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://data.stats.gov.cn/',
    'Origin': 'https://data.stats.gov.cn',
}

BASE_URL = "https://data.stats.gov.cn/dg/website/publicrelease/web/external"
ROOT_ID = "fc982599aa684be7969d7b90b1bd0e84"
MONTHLY_CODE = "1"


class StatsClient:
    """国家统计局 API V2.0 客户端"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self._tree_cache = {}       # {cache_key: (data, expire_timestamp)}
        self._indicator_cache = {}
        self._init_session()

    def _init_session(self):
        """访问首页获取 Cookie（__jsluid_s 等）"""
        try:
            logger.info("正在初始化 Session，访问首页获取 Cookie...")
            resp = self.session.get("https://data.stats.gov.cn", timeout=15)
            logger.info(f"首页访问完成，状态码: {resp.status_code}，Cookie: {dict(self.session.cookies)}")
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"首页访问失败: {e}")

    def _reinit_session(self):
        """Cookie 过期时重新初始化 Session"""
        logger.info("正在重新初始化 Session...")
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self._init_session()

    def _rate_limit(self):
        """请求间隔控制"""
        time.sleep(random.uniform(0.3, 0.6))

    def _request_with_retry(self, method, url, max_retries=3, **kwargs):
        """带重试的请求封装"""
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                resp = self.session.request(method, url, timeout=30, **kwargs)

                # 检查是否被 WAF 拦截（403 或包含 UrlACL）
                if resp.status_code == 403 or 'UrlACL' in resp.text:
                    logger.warning(f"请求被 WAF 拦截 (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        self._reinit_session()
                        continue
                    raise Exception("请求被 WAF 拦截，请稍后重试")

                resp.raise_for_status()
                return resp
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait = 2 ** attempt + random.uniform(0.5, 1.5)
                    logger.info(f"等待 {wait:.1f} 秒后重试...")
                    time.sleep(wait)
                    if attempt == 1:
                        self._reinit_session()
                    continue
                raise

    def _get_cache(self, cache_dict, key):
        """从缓存获取数据"""
        if key in cache_dict:
            data, expire_at = cache_dict[key]
            if time.time() < expire_at:
                return data
            else:
                del cache_dict[key]
        return None

    def _set_cache(self, cache_dict, key, data, ttl_seconds):
        """设置缓存"""
        cache_dict[key] = (data, time.time() + ttl_seconds)

    # ========== 指标树 API ==========

    def get_tree(self, pid=None, code="1"):
        """
        获取单层指标树
        GET /new/queryIndexTreeAsync?pid={pid}&code={code}
        """
        cache_key = f"tree_{code}_{pid or 'root'}"
        cached = self._get_cache(self._tree_cache, cache_key)
        if cached:
            logger.info(f"命中缓存: {cache_key}")
            return cached

        url = f"{BASE_URL}/new/queryIndexTreeAsync"
        params = {"pid": pid or "", "code": code}
        resp = self._request_with_retry("GET", url, params=params)
        result = resp.json()

        if not result.get("success"):
            raise Exception(f"API 返回失败: {result.get('message', '未知错误')}")

        nodes = result.get("data", [])
        self._set_cache(self._tree_cache, cache_key, nodes, 24 * 3600)
        return nodes

    def get_full_tree(self, code="1"):
        """
        递归获取完整指标树（带缓存）
        返回嵌套结构: [{ id, name, isLeaf, sdate, edate, children: [] }, ...]
        """
        logger.info("开始获取完整指标树...")

        def _build_tree(pid=None, depth=0):
            nodes = self.get_tree(pid=pid, code=code)
            result = []
            for node in nodes:
                item = {
                    "id": node["_id"],
                    "name": node.get("name") or node.get("_name", ""),
                    "isLeaf": node.get("isLeaf", False),
                    "sdate": node.get("sdate", ""),
                    "edate": node.get("edate", ""),
                }
                if not node.get("isLeaf", False):
                    item["children"] = _build_tree(node["_id"], depth + 1)
                else:
                    item["children"] = []
                result.append(item)
            return result

        tree = _build_tree()
        logger.info(f"完整指标树获取完成，共 {len(tree)} 个一级节点")
        return tree

    # ========== 指标列表 API ==========

    def get_indicators(self, cid, dt=None, name=None):
        """
        获取指定分类下的指标列表
        GET /new/queryIndicatorsByCid?cid={cid}&dt={dt}&name={name}
        """
        cache_key = f"indicators_{cid}_{dt or ''}"
        cached = self._get_cache(self._indicator_cache, cache_key)
        if cached:
            logger.info(f"命中指标缓存: {cache_key}")
            return cached

        url = f"{BASE_URL}/new/queryIndicatorsByCid"
        params = {"cid": cid, "dt": dt or "", "name": name or ""}
        resp = self._request_with_retry("GET", url, params=params)
        result = resp.json()

        if not result.get("success"):
            raise Exception(f"API 返回失败: {result.get('message', '未知错误')}")

        data = result.get("data", {})
        indicators = data.get("list", [])
        self._set_cache(self._indicator_cache, cache_key, indicators, 12 * 3600)
        return indicators

    # ========== 数据查询 API ==========

    def get_data(self, cid, indicator_ids, dts, das=None):
        """
        获取指标数据
        POST /getEsDataByCidAndDt
        """
        payload = {
            "cid": cid,
            "indicatorIds": indicator_ids,
            "das": das or [{"text": "全国", "value": "000000000000"}],
            "dts": dts,
            "showType": "1",
            "rootId": ROOT_ID,
        }

        url = f"{BASE_URL}/getEsDataByCidAndDt"
        resp = self._request_with_retry("POST", url, json=payload,
                                         headers={"Content-Type": "application/json"})
        result = resp.json()

        if not result.get("success"):
            raise Exception(f"API 返回失败: {result.get('message', '未知错误')}")

        return result.get("data", [])

    # ========== 时间范围计算 ==========

    @staticmethod
    def calc_monthly_range(months=36):
        """计算最近 N 个月的时间范围字符串，如 '202301MM-202604MM'"""
        now = datetime.now()
        end = now.strftime("%Y%m") + "MM"
        start_date = now - relativedelta(months=months - 1)
        start = start_date.strftime("%Y%m") + "MM"
        return f"{start}-{end}"

    @staticmethod
    def calc_monthly_range_dt(months=36):
        """计算 dt 参数格式，如 '2023-2026'"""
        now = datetime.now()
        end_year = now.year
        start_date = now - relativedelta(months=months - 1)
        start_year = start_date.year
        return f"{start_year}-{end_year}"
