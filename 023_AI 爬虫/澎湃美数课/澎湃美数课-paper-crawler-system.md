# 澎湃新闻「美数课」数据报告爬取系统 - 开发计划

> 项目名称：澎湃美数课数据报告爬取与管理系统
> 版本：v1.0
> 状态：待确认

---

## 一、任务理解

### 目标
针对澎湃新闻「美数课」栏目（https://www.thepaper.cn/list_25635），开发一套完整的数据爬取、展示与下载系统。系统由三部分组成：
1. **Python 代理服务器**：负责爬取数据、生成 PDF
2. **HTML 前端页面**：展示数据、提供下载功能
3. **一键启动脚本**（.bat）：自动启动服务器并打开前端

### 约束
- 每次打开 HTML 应用时自动抓取全量数据（增量更新，不重复爬取）
- 展示：封面图片、报告名称、报告网页链接
- 下载：单个报告下载 + 批量/全量下载，PDF 格式，文件名使用报告名称
- .bat 文件内容使用英文
- 所有文件放在同一文件夹下

---

## 二、网站分析结论（已完成研究）

### 2.1 页面技术架构
- **框架**：Next.js（React SSR）
- **栏目 ID**：25635（美数课）
- **渲染方式**：服务端渲染（SSR），首屏数据通过 `__NEXT_DATA__` 内嵌

### 2.2 爬取方案（三层分级）

#### ✅ 第一层：后端 API 接口（推荐方案，已确认可用）
- **端点**：`POST https://api.thepaper.cn/contentapi/nodeCont/getByNodeIdPortal`
- **请求参数**：
  ```json
  {
    "nodeId": "25635",
    "excludeContIds": [],
    "pageSize": 20,
    "startTime": 1777513927280
  }
  ```
- **响应字段**（关键字段）：
  | 字段 | 说明 |
  |------|------|
  | `contId` | 文章 ID |
  | `name` | 文章标题 |
  | `smallPic` | 缩略图 URL |
  | `pic` | 原图 URL |
  | `pubTimeLong` | 发布时间戳（毫秒） |
  | `pubTimeNew` | 格式化时间 |
  | `interactionNum` | 评论数 |
  | `contType` | 内容类型（0=图文, 9=视频） |
- **分页机制**：基于 `startTime` 时间戳的无限滚动，每页 20 条，`hasNext` 为 false 时停止
- **反爬机制**：阿里云验证码（AliyunCaptcha）、设备指纹采集

#### 第二层：HTML 解析（备用方案）
- 解析 `__NEXT_DATA__` 中的 JSON 数据
- 提取 `window.__NEXT_DATA__.props.pageProps.data.list` 数组
- 使用 BeautifulSoup 解析

#### 第三层：Browser Use 智能兜底（最终备用）
- 使用 Playwright 控制真实浏览器
- 通过截图 + 大模型视觉能力提取数据

### 2.3 详情页图片提取方案
- **详情页 URL 格式**：`https://www.thepaper.cn/newsDetail_forward_{contId}`
- **图片数据来源**：`__NEXT_DATA__` 中的 `contentDetail.images` 数组
  ```json
  {
    "imgId": 372868784,
    "src": "https://imgpai.thepaper.cn/newpai/image/xxx.jpg",
    "url": "https://imgpai.thepaper.cn/newpai/image/xxx.jpg",
    "width": 1080,
    "height": 6588
  }
  ```
- **备用方案**：解析 `<div class="cententWrap__UojXm">` 中所有 `<img>` 标签的 `data-src` 属性

---

## 三、系统架构设计

### 3.1 整体架构

```
┌──────────────┐     HTTP API      ┌──────────────────┐     HTTP/爬取     ┌─────────────┐
│  HTML 前端    │ ◄──────────────► │  Python 代理服务器  │ ◄──────────────► │  澎湃新闻 API  │
│  (浏览器)     │                   │  (Flask)          │                   │  thepaper.cn  │
└──────────────┘                   └──────────────────┘                   └─────────────┘
                                         │
                                         ▼
                                   ┌──────────────┐
                                   │  本地数据存储   │
                                   │  (JSON 文件)   │
                                   └──────────────┘
```

### 3.2 文件结构

```
项目文件夹/
├── server.py          # Python 代理服务器（Flask）
├── index.html         # 前端页面
├── start.bat          # 一键启动脚本
├── data/              # 数据存储目录（自动创建）
│   ├── reports.json   # 报告列表数据（增量更新）
│   └── pdfs/          # 生成的 PDF 文件
└── requirements.txt   # Python 依赖
```

---

## 四、PRD（产品需求文档）

### 4.1 产品概述
本产品是一个本地部署的数据爬取与管理工具，用于自动抓取澎湃新闻「美数课」栏目的全量数据报告，在浏览器中以表格形式展示，并支持将报告内容图片按顺序生成 PDF 文件下载。

### 4.2 核心功能需求

#### 功能 1：自动数据抓取
- **描述**：每次打开前端页面时，自动触发后端代理服务器抓取最新的全量数据
- **实现方式**：前端页面加载时调用后端 API `/api/fetch`，后端通过澎湃新闻 API 分页获取所有报告
- **增量更新**：后端维护本地 `reports.json`，通过 `contId` 去重，只抓取新增报告
- **预期结果**：前端展示最新全量数据，已有数据不重复抓取

#### 功能 2：数据展示表格
- **描述**：以卡片/表格形式展示所有已抓取的报告
- **展示字段**：
  - 封面图片（`smallPic` 字段，缩略图）
  - 报告名称（`name` 字段）
  - 报告网页链接（拼接为 `https://www.thepaper.cn/newsDetail_forward_{contId}`）
- **交互**：点击报告名称或图片可跳转到澎湃新闻原文页

#### 功能 3：单个报告 PDF 下载
- **描述**：用户点击某个报告的「下载 PDF」按钮，后端实时抓取该报告详情页，提取所有图片，按顺序生成 PDF
- **实现流程**：
  1. 后端请求报告详情页
  2. 从 `__NEXT_DATA__` 或 HTML 中提取图片 URL 列表
  3. 下载所有图片到临时目录
  4. 使用 Pillow/ReportLab 按顺序将图片合成 PDF
  5. PDF 文件名使用报告名称（清理非法字符）
  6. 返回 PDF 文件供下载
- **预期结果**：浏览器下载一个以报告名称命名的 PDF 文件

#### 功能 4：批量/全量 PDF 下载
- **描述**：用户可勾选多个报告或点击「全量下载」按钮，批量生成并打包下载 PDF
- **实现方式**：
  - 前端提供复选框勾选 + 「批量下载」按钮
  - 前端提供「全量下载」按钮
  - 后端将多个 PDF 打包为 ZIP 文件返回
- **预期结果**：浏览器下载一个 ZIP 文件，包含所有选中报告的 PDF

#### 功能 5：一键启动
- **描述**：运行 `start.bat` 后自动启动 Python 服务器并在浏览器中打开前端页面
- **实现方式**：bat 脚本中依次执行 `pip install`（如需要）、`python server.py`、`start http://localhost:端口`

### 4.3 交互流程

```
用户双击 start.bat
  → 自动安装 Python 依赖（首次）
  → 启动 Flask 代理服务器（端口 5000）
  → 自动打开浏览器访问 http://localhost:5000
  → 前端页面加载，自动调用 /api/reports 获取已有数据
  → 前端自动调用 /api/fetch 触发增量抓取
  → 展示报告列表（封面图 + 名称 + 链接）
  → 用户可点击「下载 PDF」下载单个报告
  → 用户可勾选多个报告后点击「批量下载」
  → 用户可点击「全量下载」下载所有报告
```

### 4.4 数据与存储
- **存储方式**：本地 JSON 文件（`data/reports.json`）
- **数据内容**：报告列表（contId、name、smallPic、pubTimeNew 等）
- **PDF 缓存**：已生成的 PDF 保存在 `data/pdfs/` 目录，避免重复生成

### 4.5 边界条件与限制
- 仅支持「美数课」栏目（nodeId=25635）
- PDF 生成依赖详情页图片可访问性
- 需要本地安装 Python 3.8+
- 需要网络连接访问澎湃新闻
- 不涉及任何 AI API 调用

### 4.6 不在本版本范围内
- 用户登录/注册功能
- 数据编辑/删除功能
- 定时自动抓取
- 其他栏目的支持
- 视频类报告的下载

---

## 五、UI 设计方案

### 5.1 整体风格
- **风格**：现代简约卡片式设计，深色主题 + 亮色强调
- **主色调**：深灰背景（#1a1a2e）+ 澎湃蓝强调色（#1e88e5）+ 白色文字
- **字体**：系统默认字体栈（-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif）
- **设计灵感**：数据仪表盘风格，突出数据报告的专业感

### 5.2 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 澎湃美数课 · 数据报告中心                    [🔄 刷新] [⬇ 全量下载] │
├─────────────────────────────────────────────────────────────────┤
│  统计栏：共 XX 篇报告 | 最近更新：YYYY-MM-DD HH:MM              │
├─────────────────────────────────────────────────────────────────┤
│  搜索框：[🔍 搜索报告名称...]              [☑ 全选] [⬇ 批量下载] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ [封面图]  │  │ [封面图]  │  │ [封面图]  │  │ [封面图]  │       │
│  │          │  │          │  │          │  │          │       │
│  │ 报告名称  │  │ 报告名称  │  │ 报告名称  │  │ 报告名称  │       │
│  │ 日期     │  │ 日期     │  │ 日期     │  │ 日期     │       │
│  │ ☑ [下载] │  │ ☑ [下载] │  │ ☑ [下载] │  │ ☑ [下载] │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ [封面图]  │  │ [封面图]  │  │ [封面图]  │  │ [封面图]  │       │
│  │ ...      │  │ ...      │  │ ...      │  │ ...      │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
│  [加载更多...] / [已加载全部 XX 篇报告]                          │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 交互设计

| 用户操作 | 界面反应 | 说明 |
|----------|----------|------|
| 页面加载 | 显示加载动画，自动抓取数据 | 增量更新，已有数据先展示 |
| 点击「🔄 刷新」 | 重新抓取最新数据 | 显示抓取进度 |
| 在搜索框输入文字 | 实时过滤报告列表 | 按名称模糊匹配 |
| 点击报告卡片 | 在新标签页打开原文链接 | `target="_blank"` |
| 勾选报告复选框 | 高亮选中卡片 | 支持多选 |
| 点击「☑ 全选」 | 勾选/取消所有报告 | 切换状态 |
| 点击「下载」按钮 | 显示生成进度，下载 PDF | 单个报告 |
| 点击「⬇ 批量下载」 | 显示打包进度，下载 ZIP | 已勾选的报告 |
| 点击「⬇ 全量下载」 | 显示打包进度，下载 ZIP | 所有报告 |
| 下载进行中 | 按钮变为进度条 + 百分比 | 禁止重复点击 |

### 5.4 组件清单

| 组件 | 用途 | 备注 |
|------|------|------|
| 顶部导航栏 | Logo + 操作按钮 | 固定顶部 |
| 统计信息栏 | 报告总数 + 更新时间 | 紧跟导航栏 |
| 搜索框 | 按名称过滤 | 实时搜索 |
| 报告卡片 | 展示封面+名称+日期+操作 | 4列网格布局 |
| 复选框 | 选择报告 | 卡片左上角 |
| 下载按钮 | 单个/批量/全量下载 | 主按钮蓝色 |
| 进度条 | 下载/生成进度 | 内联显示 |
| Toast 通知 | 操作结果反馈 | 右上角弹出 |
| 加载动画 | 数据加载中 | 骨架屏或 Spinner |

---

## 六、技术架构

### 6.1 技术栈

| 层级 | 技术选择 | 选择理由 |
|------|----------|----------|
| 后端框架 | Flask | 轻量级，适合代理服务器，单文件即可运行 |
| HTTP 请求 | requests | 成熟稳定的 HTTP 库 |
| HTML 解析 | BeautifulSoup4 | 解析详情页提取图片 |
| PDF 生成 | Pillow + ReportLab | 图片转 PDF，支持多页 |
| ZIP 打包 | zipfile（标准库） | 批量下载打包 |
| 前端 | 原生 HTML + CSS + JavaScript | 无需构建工具，直接打开 |
| 前端样式 | Tailwind CSS（CDN） | 快速开发美观界面 |
| 前端图标 | Lucide Icons（CDN） | 轻量图标库 |

### 6.2 Python 依赖（requirements.txt）
```
flask>=3.0
flask-cors>=4.0
requests>=2.31
beautifulsoup4>=4.12
Pillow>=10.0
reportlab>=4.0
```

### 6.3 后端 API 设计

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 返回 index.html 前端页面 |
| `/api/reports` | GET | 返回已缓存的报告列表 JSON |
| `/api/fetch` | POST | 触发增量抓取，返回新增数据 |
| `/api/download/<contId>` | GET | 生成并下载单个报告 PDF |
| `/api/batch-download` | POST | 批量生成 PDF 并返回 ZIP（body 为 contId 数组） |
| `/api/download-all` | GET | 全量生成 PDF 并返回 ZIP |

### 6.4 数据结构

```json
// reports.json
{
  "lastUpdate": "2026-05-27T10:00:00",
  "reports": [
    {
      "contId": "33222840",
      "name": "报告标题",
      "smallPic": "https://imgpai.thepaper.cn/...",
      "pic": "https://imgpai.thepaper.cn/...",
      "pubTimeNew": "2026/05/25",
      "pubTimeLong": 1779669997578,
      "detailUrl": "https://www.thepaper.cn/newsDetail_forward_33222840",
      "pdfGenerated": false
    }
  ]
}
```

### 6.5 关键实现说明

#### 数据抓取（三层分级策略）
1. **第一层（主方案）**：直接调用 `POST https://api.thepaper.cn/contentapi/nodeCont/getByNodeIdPortal`，携带 `nodeId`、`startTime`、`pageSize` 参数分页获取
2. **第二层（备用）**：使用 requests + BeautifulSoup 解析列表页 `__NEXT_DATA__` 中的 JSON
3. **第三层（兜底）**：使用 Playwright/Selenium 控制浏览器渲染后提取（仅在 API 失效时启用）

#### PDF 生成流程
1. 请求详情页 URL
2. 解析 `__NEXT_DATA__` JSON 中的 `contentDetail.images` 数组获取图片 URL
3. 如果 `images` 为空，回退到解析 HTML 中 `<div class="cententWrap__UojXm">` 的 `<img data-src>` 标签
4. 下载所有图片到临时目录
5. 使用 Pillow 将每张图片调整为 A4 宽度，保持比例
6. 使用 ReportLab 将图片按顺序合成多页 PDF
7. PDF 文件名清理非法字符后使用报告名称

#### 反爬应对策略
- 设置合理的 `User-Agent` 和 `Referer` 头
- 请求间隔 1-2 秒，避免触发频率限制
- 使用 `requests.Session()` 保持会话
- 如果遇到验证码拦截，自动切换到第二层/第三层方案

### 6.6 start.bat 脚本内容
```bat
@echo off
echo Starting MeiShuKe Report Crawler...
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.

:: Start server and open browser
echo Starting server...
start http://localhost:5000
python server.py

pause
```

---

## 七、开发步骤

### Step 1：创建 Python 代理服务器（server.py）
- 实现 Flask 服务器框架
- 实现三层爬取策略（API 优先，HTML 解析备用，Playwright 兜底）
- 实现增量更新逻辑（基于 contId 去重）
- 实现数据持久化（JSON 文件读写）
- 实现详情页图片提取
- 实现 PDF 生成功能
- 实现批量下载 ZIP 打包
- 配置 CORS 跨域支持

### Step 2：创建前端页面（index.html）
- 使用 Tailwind CSS 构建响应式布局
- 实现报告卡片网格展示
- 实现搜索过滤功能
- 实现全选/多选交互
- 实现下载按钮（单个/批量/全量）
- 实现加载状态和进度显示
- 实现 Toast 通知

### Step 3：创建启动脚本（start.bat）
- Python 环境检测
- 依赖自动安装
- 服务器启动
- 浏览器自动打开

### Step 4：创建依赖文件（requirements.txt）
- 列出所有 Python 依赖包

### Step 5：测试验证
- 启动服务器，验证数据抓取功能
- 验证增量更新（不重复抓取）
- 验证 PDF 生成质量
- 验证批量下载功能
- 验证一键启动脚本

---

## 八、验证标准
1. ✅ 运行 start.bat 后浏览器自动打开前端页面
2. ✅ 首次打开自动抓取全量数据并展示
3. ✅ 再次打开只抓取新增数据（增量更新）
4. ✅ 表格正确展示封面图、报告名称、链接
5. ✅ 单个报告 PDF 下载成功，图片按顺序排列
6. ✅ 批量/全量下载生成 ZIP 文件
7. ✅ PDF 文件名使用报告名称
8. ✅ 搜索过滤功能正常
9. ✅ 所有文件在同一文件夹下可正常运行
