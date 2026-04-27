# ipoipo.cn 行业报告爬虫 + 前端展示系统 — 实现计划

## 摘要

针对 `https://ipoipo.cn/category-6.html`（并购家行业报告下载站），开发一套 Python 代理服务器 + HTML 前端应用。系统自动爬取近7天全量报告数据（标题、链接、日期、真实 zip 下载地址），以深色专业数据工具风格展示，支持搜索、排序、一键下载。

---

## 当前状态分析

### 网站结构（已验证）

| 层级 | URL 模式 | 示例 | 内容 |
|------|----------|------|------|
| 列表页 | `category-6.html` / `category-6_{n}.html` | `category-6.html` | 每页约12条，共1179页 |
| 文章详情页 | `post/{id}.html` | `post/26011.html` | 标题、正文、下载链接 |
| 下载页 | `download/{id}.html` | `download/26011.html` | 真实 zip 地址 |
| ZIP 文件 | `zb_users/upload/YYYY/MM/{timestamp}.zip` | `zb_users/upload/2025/12/202512010947311774910.zip` | 最终下载目标 |

**关键发现**：
- 纯静态 HTML，**无 AJAX/API 接口**
- 列表页每条记录包含：标题（`<h2>` 内 `<a>`）、链接、日期（`YYYY-MM-DD`）、缩略图
- 详情页中"下载地址"链接指向 `download/{id}.html`
- 下载页中包含指向真实 zip 文件的 `<a>` 标签
- 近7天数据分布在第1-2页（约20-30条记录）

---

## 文件结构

```
/workspace/ipoipo-scraper/
├── server.py              # Flask 代理服务器（主程序）
├── scraper.py             # 爬虫核心逻辑模块
├── requirements.txt       # Python 依赖
├── templates/
│   └── index.html         # 前端单页应用
└── cache/                 # 数据缓存目录（自动创建）
    └── reports.json       # 缓存的报告数据
```

---

## 实现步骤

### 步骤 1: 创建项目结构和依赖

- 创建 `/workspace/ipoipo-scraper/` 目录结构
- 编写 `requirements.txt`：`flask`, `requests`, `beautifulsoup4`, `lxml`

### 步骤 2: 实现 `scraper.py` 爬虫模块

**IPOScraper 类核心方法**：

1. **`fetch_recent_reports(days=7)`** — 主入口
   - 从第1页开始遍历列表页
   - 解析每条记录的标题、链接、日期、文章ID
   - 遇到日期早于7天前的记录时停止翻页
   - 对每条记录访问 `download/{id}.html` 获取真实 zip 地址
   - 返回按日期降序+标题升序排列的报告列表

2. **`_parse_list_page(soup)`** — 解析列表页
   - 使用 CSS 选择器定位文章容器
   - 提取：标题（`h2 > a`）、链接（`href`）、日期（正则匹配 `YYYY-MM-DD`）、文章ID（从链接中提取）
   - 需先 `curl` 获取原始 HTML 确认精确 DOM 结构

3. **`_get_download_url(post_id)`** — 获取真实下载地址
   - 访问 `download/{id}.html`
   - 用 `soup.find('a', href=re.compile(r'\.zip$'))` 提取 zip 链接
   - 已验证此方法可行

4. **反爬策略**：
   - 真实浏览器 `User-Agent` + `Referer` 头
   - 每页请求间隔 1-2 秒
   - `timeout=15` 防阻塞
   - 异常重试（最多3次）

### 步骤 3: 实现 `server.py` Flask 服务器

**API 端点设计**：

| 端点 | 方法 | 功能 | 参数 | 响应 |
|------|------|------|------|------|
| `/` | GET | 返回前端 HTML | 无 | HTML |
| `/api/reports` | GET | 获取近7天报告 | `days`（可选） | JSON |
| `/api/reports/refresh` | GET | 强制刷新缓存 | `days`（可选） | JSON |
| `/api/proxy/download` | GET | 代理下载 zip | `url`（zip地址） | 文件流 |

**缓存机制**：
- JSON 文件缓存，TTL = 1小时
- `/api/reports/refresh` 清除缓存并重新爬取

**代理下载**：
- 使用 `stream=True` 流式传输，避免大文件内存问题
- 设置正确的 `Content-Disposition` 头

### 步骤 4: 实现 `templates/index.html` 前端

**设计方向**：专业数据工具风格（类似 Bloomberg Terminal）
- **配色**：深色主题 `#0f1117` 底色，`#00c9a7` 青绿强调色
- **字体**：`JetBrains Mono`（数字）+ `Noto Sans SC`（中文）
- **布局**：紧凑表格式数据展示

**页面结构**：
```
┌──────────────────────────────────────────────────┐
│ HEADER: 行业报告速递 | 更新时间 | 刷新按钮       │
├──────────────────────────────────────────────────┤
│ TOOLBAR: 搜索框 | 排序切换 | 统计数字            │
├──────────────────────────────────────────────────┤
│ TABLE: 序号 | 日期 | 标题 | 页数 | 下载按钮      │
├──────────────────────────────────────────────────┤
│ FOOTER: 数据来源 ipoipo.cn | 共 N 条报告         │
└──────────────────────────────────────────────────┘
```

**核心功能**：
1. 页面打开自动 `fetch('/api/reports')` 获取数据
2. 实时搜索过滤（debounce 300ms）
3. 排序切换（日期升/降序、标题 A-Z）
4. 下载按钮通过 `/api/proxy/download` 代理下载
5. 加载骨架屏 + 进度提示
6. 错误友好提示
7. 从标题提取页数 `（XX页）`

### 步骤 5: 集成测试

1. 启动服务器 `python server.py`
2. 浏览器访问 `http://localhost:5000`
3. 验证：数据加载、搜索、排序、下载
4. 边界测试：无数据、网络异常、下载失败

---

## 假设与决策

| 决策 | 理由 |
|------|------|
| 使用 Flask 而非 FastAPI | 轻量、成熟、模板渲染简单 |
| 串行爬取而非并发 | 近7天约26次请求，串行足够快且更安全 |
| JSON 文件缓存而非数据库 | 数据量小（<100条），无需数据库 |
| 代理下载而非直链 | 解决跨域和可能的防盗链问题 |
| 深色主题 | 专业数据工具感，避免 AI 通用审美 |
| 缓存 TTL 1小时 | 平衡实时性和服务器负载 |

---

## 验证步骤

1. **爬虫验证**：运行 `scraper.py` 单独测试，确认能正确解析列表页和下载页
2. **API 验证**：`curl http://localhost:5000/api/reports` 检查 JSON 响应格式
3. **前端验证**：浏览器打开页面，检查数据展示、搜索、排序功能
4. **下载验证**：点击下载按钮，确认 zip 文件可正常下载和解压
5. **缓存验证**：首次请求后再次请求，确认响应时间显著缩短
6. **刷新验证**：点击刷新按钮，确认数据重新爬取
