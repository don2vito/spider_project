# 易观分析报告爬取与展示系统 — 开发计划

> 状态：待确认
> 日期：2026-05-26

---

## 一、任务理解

### 1.1 目标
构建一个本地运行的系统，爬取易观分析网站 (`analysys.cn/article/analysis/`) 的全量数据报告（约 3,930 篇），通过 Python Flask 代理服务器提供数据查询和 PDF 下载功能，配合单页 HTML 前端进行可视化展示和下载管理。

### 1.2 核心需求
1. **三层爬取策略**：API 接口提取 → HTML 解析 → Browser Use 兜底
2. **全量数据爬取**：报告标题、链接、报告内容（图片），不重复爬取
3. **前端展示**：表格展示封面图片、报告名称、报告网页链接
4. **下载功能**：单独下载 + 批量下载 + 全量下载，根据报告详情页图片按顺序生成 PDF
5. **一键启动**：.bat 文件启动代理服务器并打开前端页面
6. **文档输出**：完整的 PRD 和 UI 方案（Markdown 格式）

### 1.3 约束条件
- .bat 文件内容使用英文
- PDF 文件名使用报告名称
- Python 代理服务器 + HTML 前端应用架构
- .bat、Python 代码、HTML 文件在同一文件夹下

---

## 二、网站研究结果

### 2.1 渲染方式
- **SSR（服务端渲染）**：数据嵌入在 `window.__INITIAL_STATE__` JSON 中
- 技术栈：Vue.js + Webpack + SSR

### 2.2 分页机制
- URL 参数分页：`?p=N`，共 **393 页**，每页 **10 篇**，总计 **3,930 篇**
- 无 Ajax 动态加载，传统页面跳转

### 2.3 关键数据字段
| 字段 | 说明 |
|------|------|
| `id` | 文章 ID |
| `maintitle` | 文章标题 |
| `summary` | 文章摘要 |
| `classify` | 分类标签 |
| `field` | 领域 |
| `source` | 来源 |
| `author` | 作者 |
| `clickcount` | 阅读量 |
| `publishdate` | 发布时间 |
| `images` | 图片列表（PDF 转图片） |
| `articleext1` | PDF 附件路径 |

### 2.4 详情页结构
- URL 格式：`/article/detail/{id}`
- 报告内容以 **PDF 转图片** 方式展示
- 图片 URL：`https://www.analysys.cn/uploadcmsimages/...`，可直接下载无需认证
- PDF 原文件下载需要登录

### 2.5 反爬机制
| 防护类型 | 严重程度 |
|----------|----------|
| 网易易盾验证码 SDK | 中-高 |
| 登录墙（PDF 下载） | 中 |
| 百度统计 / GTM 埋点 | 低 |
| 无严格频率限制 | - |

### 2.6 爬取方案结论
- **无公开 API**：所有数据通过 SSR 注入
- **第一层（推荐）**：正则提取 `window.__INITIAL_STATE__` 中的 JSON 数据
- **第二层（备用）**：BeautifulSoup 解析 HTML DOM
- **第三层（兜底）**：Playwright 控制真实浏览器

---

## 三、技术架构

### 3.1 技术栈
| 层级 | 技术选择 | 理由 |
|------|---------|------|
| 后端框架 | Flask | 轻量、易部署、适合代理服务器 |
| 爬虫核心 | requests + BeautifulSoup + re | 覆盖三层策略 |
| 浏览器兜底 | Playwright | 无头浏览器自动化 |
| PDF 生成 | img2pdf | 轻量、无损、速度快 |
| 数据存储 | SQLite | 零配置、单文件、适合本地应用 |
| 前端 | 原生 HTML + CSS + JavaScript | 无需构建工具、直接打开 |
| 启动脚本 | .bat (Windows) | 一键启动 |

### 3.2 项目文件结构
```
analysys-crawler/
├── start.bat                    # 一键启动脚本（英文）
├── requirements.txt             # Python 依赖
├── app.py                       # Flask 主入口
├── config.py                    # 全局配置
├── crawler/                     # 爬虫模块
│   ├── __init__.py
│   ├── base.py                  # 爬虫基类
│   ├── layer1_extractor.py      # 第一层：正则提取 __INITIAL_STATE__
│   ├── layer2_parser.py         # 第二层：BeautifulSoup HTML 解析
│   ├── layer3_browser.py        # 第三层：Playwright 浏览器兜底
│   ├── dispatcher.py            # 三层调度器
│   ├── image_downloader.py      # 图片下载器
│   └── rate_limiter.py          # 频率控制
├── models/
│   ├── __init__.py
│   └── database.py              # SQLite 数据库操作
├── services/
│   ├── __init__.py
│   ├── crawl_service.py         # 爬取调度服务
│   └── pdf_service.py           # PDF 生成服务
├── api/
│   ├── __init__.py
│   ├── list_api.py              # 列表接口
│   ├── detail_api.py            # 详情接口
│   ├── download_api.py          # 下载接口
│   └── crawl_api.py             # 爬取控制接口
├── templates/
│   └── index.html               # 前端单页应用
├── data/                        # 运行时数据
│   ├── analysys.db              # SQLite 数据库
│   ├── images/                  # 报告图片缓存
│   └── pdfs/                    # 生成的 PDF
└── logs/                        # 日志
```

---

## 四、实施步骤

### 步骤 1：生成 PRD 和 UI 方案文档
- 基于研究结果，生成完整的 `PRD.md` 和 `UI_DESIGN.md`
- 输出为 Markdown 格式，保存到 `/workspace`

### 步骤 2：项目骨架搭建
- 创建目录结构
- 编写 `config.py`、`requirements.txt`
- 编写 `models/database.py`，完成 SQLite 建表和 CRUD
- 编写 `app.py` 基础框架，验证 Flask 启动

### 步骤 3：三层爬虫实现
- 编写 `crawler/rate_limiter.py`（频率控制）
- 编写 `crawler/base.py`（爬虫基类）
- 编写 `crawler/layer1_extractor.py`（正则提取 `__INITIAL_STATE__`）
- 编写 `crawler/layer2_parser.py`（BeautifulSoup HTML 解析）
- 编写 `crawler/layer3_browser.py`（Playwright 浏览器兜底）
- 编写 `crawler/dispatcher.py`（三层降级调度器）
- 编写 `crawler/image_downloader.py`（图片下载器）

### 步骤 4：业务服务层
- 编写 `services/crawl_service.py`（全量/增量爬取调度）
- 编写 `services/pdf_service.py`（图片合成 PDF）

### 步骤 5：API 接口层
- 编写 `api/list_api.py`（报告列表、分类筛选、搜索）
- 编写 `api/detail_api.py`（报告详情、图片列表）
- 编写 `api/download_api.py`（单独/批量/全量下载）
- 编写 `api/crawl_api.py`（爬取状态控制）

### 步骤 6：前端 HTML 应用
- 编写 `templates/index.html`（页面结构）
- 实现表格展示（封面图片、报告名称、链接）
- 实现搜索、分类筛选、分页
- 实现下载功能（单独/批量/全量）
- 实现爬取控制面板和进度展示

### 步骤 7：启动脚本与集成
- 编写 `start.bat`（一键启动，英文内容）
- 图片代理端点（解决跨域）
- 端到端测试

### 步骤 8：测试与交付
- 爬取前几页数据验证
- PDF 生成和下载测试
- 批量下载测试
- 全量爬取测试

---

## 五、关键设计决策

### 5.1 数据去重策略
- 使用 SQLite，以文章 `id` 为主键
- `INSERT OR IGNORE` 避免重复插入
- `crawl_status` 字段追踪爬取状态，支持断点续爬

### 5.2 图片到 PDF 转换
- 使用 `img2pdf` 库，直接将 JPEG/PNG 嵌入 PDF
- 图片按三位数序号命名（001.jpg, 002.jpg...）保证顺序
- PDF 文件名使用报告名称（清理非法字符）

### 5.3 反爬应对
- 随机请求间隔 1.5-3 秒
- User-Agent 轮换
- 指数退避重试（最多 3 次）
- 失败自动降级到下一层

### 5.4 大批量下载
- 批量下载返回 ZIP 文件
- 全量下载使用后台线程 + 进度轮询
- 分批处理（每批 50 篇）

---

## 六、风险与应对

| 风险 | 应对措施 |
|------|---------|
| `__INITIAL_STATE__` 结构变化 | 三层自动降级 |
| 网易易盾验证码拦截 | 降低频率；Playwright 层可手动处理 |
| 图片 URL 失效 | 记录失败状态，支持重试 |
| 全量数据磁盘占用大（预估 8-20 GB） | 提供磁盘空间检查；支持选择性下载 |
| 网站反爬升级 | 三层降级策略；预留扩展接口 |
