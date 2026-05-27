# 产品需求文档（PRD）

> 项目名称：易观分析报告爬取与展示系统
> 版本：v1.0
> 状态：✅ 已确认
> 日期：2026-05-26

---

## 一、产品概述

易观分析报告爬取与展示系统是一个本地运行的数据采集与管理工具。它通过三层降级爬取策略（正则提取 SSR 数据 → HTML DOM 解析 → Playwright 浏览器自动化），从易观分析网站（`analysys.cn/article/analysis/`）全量采集约 3,930 篇行业分析报告的元数据和内容图片，通过 Python Flask 代理服务器提供数据查询、图片预览和 PDF 下载功能，配合单页 HTML 前端实现可视化展示和批量管理。

**目标用户**：需要批量获取易观分析行业报告的研究人员、咨询顾问、市场分析师。

**核心价值**：一键启动、自动爬取、全量下载、离线阅读。

---

## 二、核心功能需求

### 功能 1：全量数据爬取

- **描述**：系统自动爬取易观分析网站 `/article/analysis/` 下所有报告的元数据和内容图片
- **爬取范围**：约 393 页，每页 10 篇，总计约 3,930 篇报告
- **采集字段**：
  - 报告标题（`maintitle`）
  - 报告链接（`/article/detail/{id}`）
  - 报告摘要（`summary`）
  - 分类标签（`classify`）
  - 领域（`field`）
  - 来源（`source`）
  - 作者（`author`）
  - 阅读量（`clickcount`）
  - 发布时间（`publishdate`）
  - 报告内容图片列表（`images`）
- **去重机制**：基于文章 ID 去重，已爬取的数据不会重复采集
- **断点续爬**：记录每篇文章的爬取状态（未爬取 / 已爬取 / 失败），重启后从断点继续
- **用户操作**：用户点击「开始爬取」按钮启动，可随时查看爬取进度，可暂停/停止
- **预期结果**：前端实时展示爬取进度（已爬取页数/总页数、已爬取文章数、成功/失败数）

### 功能 2：报告列表展示

- **描述**：以表格形式展示所有已爬取的报告
- **展示字段**：封面图片（缩略图）、报告名称、分类标签、发布时间、操作按钮
- **交互功能**：
  - 关键词搜索（搜索报告标题）
  - 分类筛选（下拉框选择分类标签）
  - 分页浏览（每页 20 条，支持翻页）
  - 全选/取消全选（用于批量操作）
- **用户操作**：用户在搜索框输入关键词或选择分类进行筛选，点击翻页按钮浏览
- **预期结果**：表格实时更新，展示符合条件的报告列表

### 功能 3：报告详情查看

- **描述**：点击报告名称可跳转到易观分析网站的原始报告页面
- **用户操作**：用户点击报告名称链接
- **预期结果**：在新标签页中打开报告详情页

### 功能 4：单独下载报告

- **描述**：将单篇报告的内容图片按顺序合成为 PDF 文件并下载
- **PDF 文件名**：使用报告名称（自动清理文件名中的非法字符）
- **用户操作**：用户点击某篇报告的「下载」按钮
- **预期结果**：
  - 如果图片已下载，直接生成 PDF 并触发浏览器下载
  - 如果图片未下载，先下载图片再生成 PDF
  - 下载的 PDF 文件名格式为：`{报告名称}.pdf`

### 功能 5：批量下载报告

- **描述**：将用户选中的多篇报告分别生成 PDF，打包为 ZIP 文件下载
- **用户操作**：
  1. 用户勾选多篇报告（通过复选框）
  2. 点击「批量下载」按钮
- **预期结果**：浏览器下载一个 ZIP 文件，内含每篇报告的 PDF（文件名：`{报告名称}.pdf`）

### 功能 6：全量下载报告

- **描述**：将所有已爬取报告生成 PDF 并打包下载
- **用户操作**：用户点击「全量下载」按钮
- **预期结果**：
  - 弹出确认对话框，提示全量下载的预估大小和时间
  - 确认后启动后台任务，前端显示进度条
  - 完成后自动触发 ZIP 文件下载

### 功能 7：爬取状态监控

- **描述**：实时展示爬取任务的进度和统计信息
- **展示内容**：
  - 总报告数 / 已爬取数 / 爬取失败数
  - 已下载图片数 / 已生成 PDF 数
  - 当前爬取页码 / 总页码
  - 爬取速度（篇/分钟）
- **用户操作**：页面顶部统计栏自动刷新
- **预期结果**：统计数据每 5 秒自动更新

---

## 三、交互流程

### 3.1 首次使用流程

```
用户双击 start.bat
  → 系统检查 Python 环境
  → 自动创建虚拟环境并安装依赖（首次）
  → 启动 Flask 服务器
  → 自动打开浏览器访问 http://127.0.0.1:5000
  → 前端页面加载，显示空数据表格
  → 用户点击「开始爬取」
  → 后台开始爬取，前端实时显示进度
  → 爬取完成后，表格展示全量数据
```

### 3.2 日常使用流程

```
用户双击 start.bat
  → Flask 服务器启动，自动打开浏览器
  → 前端加载已缓存的数据（从 SQLite）
  → 用户浏览、搜索、筛选报告
  → 用户选择下载方式（单独/批量/全量）
  → 下载完成
```

### 3.3 下载报告流程（单篇）

```
用户点击「下载」按钮
  → 前端发送请求到 /api/download/{article_id}
  → 后端检查图片是否已下载
    → 未下载：下载图片到本地（data/images/{article_id}/）
  → 后端使用 img2pdf 将图片合成为 PDF
  → 返回 PDF 文件流
  → 浏览器触发下载，文件名为 {报告名称}.pdf
```

### 3.4 异常处理流程

```
爬取过程中网络中断
  → 记录失败页码到数据库
  → 自动重试 3 次（指数退避）
  → 3 次均失败则标记为「失败」，跳过继续
  → 用户可手动触发「重新爬取失败项」

图片下载失败
  → 记录失败图片到数据库
  → PDF 生成时跳过缺失图片
  → 日志记录缺失信息

磁盘空间不足
  → 下载前检查剩余空间
  → 不足时弹出警告提示
```

---

## 四、数据与存储

### 4.1 存储方式
- **数据库**：SQLite（单文件 `data/analysys.db`）
- **图片缓存**：本地文件系统（`data/images/{article_id}/`）
- **PDF 文件**：本地文件系统（`data/pdfs/`）

### 4.2 数据库表结构

**articles 表（报告元数据）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 文章 ID（来自网站） |
| maintitle | TEXT | 报告标题 |
| summary | TEXT | 摘要 |
| classify | TEXT | 分类标签 |
| field | TEXT | 领域 |
| source | TEXT | 来源 |
| author | TEXT | 作者 |
| clickcount | INTEGER | 阅读量 |
| publishdate | TEXT | 发布时间 |
| cover_image | TEXT | 封面图片 URL |
| detail_url | TEXT | 详情页 URL |
| crawl_status | INTEGER | 0:未爬取详情 1:已爬取 2:失败 |
| image_count | INTEGER | 图片数量 |
| pdf_status | INTEGER | 0:未生成 1:已生成 2:失败 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**article_images 表（报告图片）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| article_id | INTEGER FK | 关联文章 ID |
| page_number | INTEGER | 页码顺序 |
| image_url | TEXT | 原始图片 URL |
| local_path | TEXT | 本地存储路径 |
| download_status | INTEGER | 0:未下载 1:已下载 2:失败 |
| file_size | INTEGER | 文件大小（字节） |

**crawl_logs 表（爬取日志）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| log_type | TEXT | list / detail / image / pdf |
| article_id | INTEGER | 关联文章 ID |
| status | TEXT | success / error / skip |
| message | TEXT | 日志信息 |
| created_at | TIMESTAMP | 记录时间 |

### 4.3 数据格式
- 所有文本使用 UTF-8 编码
- 日期格式：`YYYY-MM-DD HH:MM:SS`
- 图片格式：PNG / JPEG
- PDF 格式：标准 PDF 1.4+

---

## 五、API 接口设计

### 5.1 报告列表

```
GET /api/articles?page=1&per_page=20&keyword=xxx&classify=xxx

Response:
{
  "code": 0,
  "data": {
    "articles": [...],
    "total": 3930,
    "page": 1,
    "per_page": 20,
    "total_pages": 197
  }
}
```

### 5.2 报告详情

```
GET /api/articles/{article_id}

Response:
{
  "code": 0,
  "data": {
    "article": {...},
    "images": [...]
  }
}
```

### 5.3 单篇下载

```
GET /api/download/{article_id}

Response: PDF 文件流（Content-Type: application/pdf）
```

### 5.4 批量下载

```
POST /api/download/batch
Body: { "article_ids": [20021458, 20021457, ...] }

Response: ZIP 文件流（Content-Type: application/zip）
```

### 5.5 全量下载

```
POST /api/download/all

Response:
{
  "code": 0,
  "data": { "task_id": "uuid" }
}

GET /api/download/progress/{task_id}

Response:
{
  "code": 0,
  "data": {
    "total": 3930,
    "completed": 150,
    "status": "running"
  }
}
```

### 5.6 爬取控制

```
POST /api/crawl/start
Body: { "start_page": 1, "end_page": 393, "mode": "full" }

GET /api/crawl/status

Response:
{
  "code": 0,
  "data": {
    "is_running": true,
    "current_page": 15,
    "total_pages": 393,
    "articles_found": 150,
    "articles_detail": 80,
    "images_downloaded": 1200,
    "errors": 3
  }
}

POST /api/crawl/stop
```

### 5.7 图片代理

```
GET /proxy/image?url={encoded_url}

Response: 图片二进制流（解决前端跨域问题）
```

### 5.8 分类列表

```
GET /api/classifies

Response:
{
  "code": 0,
  "data": ["焦点专题分析", "行业监测分析", "趋势预测分析", ...]
}
```

---

## 六、三层爬取策略详解

### 6.1 第一层：正则提取 `window.__INITIAL_STATE__`

- **原理**：网站采用 SSR，页面 HTML 中嵌入 `window.__INITIAL_STATE__={...}` JSON 数据
- **方法**：使用正则表达式 `window\.__INITIAL_STATE__\s*=\s*(\{.*?\});` 提取 JSON，解析后直接获取结构化数据
- **优势**：速度最快、数据最完整、无需解析 DOM
- **适用场景**：网站保持 SSR 渲染方式

### 6.2 第二层：BeautifulSoup HTML 解析

- **原理**：当 `__INITIAL_STATE__` 不存在或格式变化时，直接解析 HTML DOM 结构
- **方法**：使用 BeautifulSoup 解析 HTML，通过 CSS 选择器定位文章列表容器，提取标题、链接、摘要等字段
- **优势**：对 HTML 结构变化有一定容忍度
- **适用场景**：网站改版但仍为 SSR

### 6.3 第三层：Playwright 浏览器自动化

- **原理**：当静态抓取完全失效时（如引入 JS 加密、强验证码），使用无头浏览器模拟真实用户
- **方法**：Playwright 启动 Chromium，加载页面，等待渲染完成后从 DOM 或 `window.__INITIAL_STATE__` 提取数据
- **优势**：最接近真实用户行为，可处理 JS 动态渲染和简单验证码
- **适用场景**：网站升级为 CSR 或引入强反爬

### 6.4 降级调度逻辑

```
请求列表页/详情页
  → 尝试第一层（正则提取）
    → 成功：返回数据
    → 失败：尝试第二层（HTML 解析）
      → 成功：返回数据，记录日志
      → 失败：尝试第三层（Playwright）
        → 成功：返回数据，记录告警
        → 失败：返回 None，记录错误
```

---

## 七、边界条件与限制

1. **网络依赖**：爬取过程需要稳定的网络连接，断网时自动暂停并记录进度
2. **磁盘空间**：全量图片缓存预估 8-20 GB，PDF 文件预估 4-10 GB，需确保足够磁盘空间
3. **爬取速度**：为避免触发反爬，请求间隔 1.5-3 秒，全量爬取约需 3-5 小时
4. **图片质量**：报告图片为网站提供的预览图（PDF 转图片），分辨率取决于原始 PDF
5. **付费报告**：部分报告标记为付费内容（`isFree: 0`），图片预览可能不完整
6. **网站变更**：网站结构可能随时变更，三层降级策略可应对部分变更
7. **并发限制**：图片下载最大并发 3 个线程，避免触发频率限制
8. **浏览器兼容**：前端应用支持 Chrome、Firefox、Edge 等现代浏览器

---

## 八、不在本版本范围内

1. 用户登录/注册功能
2. 报告内容全文搜索（仅支持标题搜索）
3. 报告内容 OCR 文字识别
4. 数据导出为 Excel/CSV
5. 定时自动爬取（需手动触发）
6. 多语言支持
7. 移动端适配
8. 报告内容在线阅读（仅支持下载 PDF）
9. 爬取规则自定义配置界面
10. 分布式爬取支持

---

## 九、开发工具与环境

- **开发工具**：Cursor / Trae / VS Code
- **Python 版本**：3.8+
- **运行方式**：本地启动 Flask 服务器，浏览器访问 `http://127.0.0.1:5000`
- **操作系统**：Windows（.bat 启动）/ Linux / macOS
- **依赖管理**：pip + requirements.txt + venv 虚拟环境

---

## 十、Python 依赖清单

```
flask==3.0.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==5.1.0
img2pdf==0.5.1
Pillow==10.2.0
playwright==1.40.0
```
