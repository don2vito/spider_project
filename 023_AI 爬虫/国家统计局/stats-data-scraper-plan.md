# 国家统计局月度数据抓取与查看系统 — 实施计划

## 摘要

构建一个由 **Python Flask 代理服务器** + **单文件 HTML 前端应用** 组成的系统，用于从国家统计局网站 (`data.stats.gov.cn`) 抓取月度统计数据。用户在 HTML 页面中通过层级树勾选指标，一键获取最近 36 个月数据，按指标名称升序展示，并支持导出 Excel。

---

## 当前状态分析

### 目标网站结构
- **URL**: `https://data.stats.gov.cn/dg/website/page.html#/pc/national/monthData`
- **新版 API V2.0 基础路径**: `https://data.stats.gov.cn/dg/website/publicrelease/web/external`
- **月度数据根节点 ID**: `fc982599aa684be7969d7b90b1bd0e84`，分类代码 `code=1`
- **指标树层级**: 月度数据 → 14 个一级分类 → 子分类 → 指标组 → 具体指标（叶子节点 `isLeaf=true`）
- **WAF 防护**: 网站部署了 WAF，需要携带 Cookie（`__jsluid_s`）和浏览器请求头才能访问 API

### 三个核心 API 端点

| 功能 | 方法 | 路径 | 关键参数 |
|------|------|------|----------|
| 指标树 | GET | `/new/queryIndexTreeAsync` | `pid`（父节点ID）, `code=1` |
| 指标列表 | GET | `/new/queryIndicatorsByCid` | `cid`（叶子节点ID）, `dt`（时间范围）, `name` |
| 数据查询 | POST | `/getEsDataByCidAndDt` | JSON body: `cid`, `indicatorIds[]`, `das[]`, `dts[]` |

### 时间编码格式
- 月度范围: `"202301MM-202604MM"`（起止年月 + MM 后缀）
- 需动态计算最近 36 个月的范围

---

## 文件结构

```
/workspace/
├── proxy/
│   ├── app.py              # Flask 主应用，路由定义
│   ├── stats_client.py     # 国家统计局 API V2.0 客户端封装
│   └── requirements.txt    # Python 依赖 (flask, flask-cors, requests)
└── viewer.html             # 单文件 HTML 前端应用
```

---

## 详细实施方案

### 第 1 步：搭建 Python 代理基础框架

**文件**: `proxy/requirements.txt`, `proxy/app.py`, `proxy/stats_client.py`

- 创建 `requirements.txt`，依赖: `flask`, `flask-cors`, `requests`
- 创建 `stats_client.py`，实现 `StatsClient` 类骨架：
  - `requests.Session()` 维持 Cookie
  - 首次使用前 GET `https://data.stats.gov.cn` 首页获取 `__jsluid_s` Cookie
  - 请求头伪装: `User-Agent`, `Referer`, `Origin`, `Accept`
  - 速率控制: 每次请求间隔 `random.uniform(0.3, 0.6)` 秒
  - 3 次重试 + 指数退避
- 创建 `app.py`，Flask 应用 + `CORS()` 全局允许 + 三个路由占位

### 第 2 步：实现指标树获取与缓存

**文件**: `proxy/stats_client.py`

- 实现 `get_tree(pid, code)` — 单层树获取
- 实现 `get_full_tree(code="1")` — 递归获取完整指标树
- 内存缓存: 字典 + TTL（树结构 24 小时，指标列表 12 小时）
- 返回结构: `{ id, name, isLeaf, sdate, edate, children: [] }`

### 第 3 步：实现指标列表与数据查询

**文件**: `proxy/stats_client.py`

- 实现 `get_indicators(cid, dt, name)` — GET 请求获取指标列表
- 实现 `get_data(cid, indicator_ids, dts)` — POST 请求获取数据
  - 请求体: `{ cid, indicatorIds, das: [{"text":"全国","value":"000000000000"}], dts: ["202301MM-202604MM"], showType: "1", rootId: "fc982599aa684be7969d7b90b1bd0e84" }`
- 实现 `calc_monthly_range(months=36)` — 动态计算时间范围
- **Cookie 过期处理**: 如果 POST 返回 403/空数据，自动重新初始化 Session 并重试

### 第 4 步：完善 Flask 路由

**文件**: `proxy/app.py`

三个 API 路由:

| 路由 | 方法 | 功能 |
|------|------|------|
| `/api/tree` | GET | 返回完整月度指标树 |
| `/api/indicators` | GET | 参数 `cid`, `dt`，返回指标列表 |
| `/api/data` | POST | 参数 `{ cids: [], months: 36 }`，批量获取数据 |

`/api/data` 内部逻辑: 遍历 cids → 逐个获取指标列表 → 逐个获取数据 → 汇总返回。单个 cid 失败不影响其他。

### 第 5 步：实现 HTML 前端 — 页面布局与指标树

**文件**: `viewer.html`

- 引入 Tailwind CSS CDN + SheetJS CDN
- 左右分栏布局: 左侧指标树面板（280px 固定宽度）+ 右侧数据区域
- 页面顶部: 标题 + 时间范围显示 + 操作按钮
- 实现 `buildTree()` 函数: 递归渲染嵌套树，每个节点带 checkbox + 展开/折叠箭头
- 启动时 fetch `/api/tree` 加载指标树

### 第 6 步：实现 HTML 前端 — 选中逻辑

**文件**: `viewer.html`

- 父子联动: 勾选父节点 → 自动勾选所有子节点；子节点部分选中 → 父节点 indeterminate 状态
- 全选/取消全选按钮
- 选中叶子节点计数实时显示
- 仅叶子节点（`isLeaf=true`）参与数据查询

### 第 7 步：实现 HTML 前端 — 数据获取与表格展示

**文件**: `viewer.html`

- 点击"获取数据"按钮 → 收集选中叶子节点 cid → POST `/api/data`
- 加载状态: 进度条 + 文字提示（正在获取第 N/M 个指标...）
- 表格渲染: 按指标名称升序排列，每个指标的数据追加在前一个下方
- 时间列作为表头，行为指标+数值
- 空数据/错误状态友好提示

### 第 8 步：实现 HTML 前端 — Excel 导出

**文件**: `viewer.html`

- 使用 SheetJS (`XLSX.utils.table_to_book`) 将表格导出为 `.xlsx`
- 文件名格式: `国家统计局月度数据_YYYY-MM-DD.xlsx`
- 导出前确认有数据

### 第 9 步：UI 打磨与响应式适配

**文件**: `viewer.html`

- 桌面端: 左右分栏；平板端: 树面板可折叠；移动端: 树面板抽屉式
- 表格窄屏横向滚动
- 深色/浅色主题切换（可选）
- 微交互动画（展开/折叠、加载过渡）

### 第 10 步：测试与验证

- 启动代理服务器，验证三个 API 路由正常工作
- 在浏览器打开 `viewer.html`，验证完整流程:
  1. 指标树加载并正确展示层级结构
  2. 勾选指标后父子联动正确
  3. 点击获取数据后表格正确渲染
  4. 数据按指标名称升序排列
  5. Excel 导出功能正常
- 边界测试: Cookie 过期自动恢复、大量指标选择、无数据指标、网络异常

---

## 假设与决策

| 决策 | 选择 | 理由 |
|------|------|------|
| Web 框架 | Flask | 轻量、简单，适合代理服务器场景 |
| 前端框架 | 原生 JS + Tailwind CSS | 单文件要求，无需构建工具 |
| Excel 导出 | SheetJS (CDN) | 浏览器端直接生成，无需后端参与 |
| API 版本 | 新版 V2.0 | 支持批量查询，数据更丰富 |
| Cookie 策略 | requests.Session + 首页预访问 | 简单有效，无需浏览器自动化 |
| 降级方案 | Cookie 过期时自动重新初始化 | 优雅处理，无需额外依赖 |

---

## 验证步骤

1. `cd proxy && pip install -r requirements.txt && python app.py` — 服务器启动无报错
2. `curl http://localhost:5000/api/tree` — 返回完整指标树 JSON
3. 浏览器打开 `viewer.html` — 左侧显示 14 个一级分类的树结构
4. 勾选"价格指数" → 所有子指标自动选中 → 计数更新
5. 点击"获取数据" → 进度条显示 → 表格按指标名称升序渲染数据
6. 点击"导出 Excel" → 下载 `.xlsx` 文件，内容与页面表格一致
