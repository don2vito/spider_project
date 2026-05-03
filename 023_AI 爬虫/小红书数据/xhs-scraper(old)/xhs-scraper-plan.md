# 小红书数据采集系统 — 实现计划

## 摘要

构建一套完整的小红书网页数据采集系统，包含 Python 代理服务器（Flask签名服务 + FastAPI主服务）、精美HTML前端应用、一键启动BAT脚本。支持关键词搜索和作者搜索，可抓取笔记全量数据（标题、链接、发布时间、内容、图片、视频、评论、回复、点赞/收藏/评论数），提供单篇/批量ZIP下载和四维数据分析（统计图表、词云关键词、时间趋势、情感分析）。

---

## 当前状态分析

- 小红书Web端采用高强度反爬：X-s/X-t动态签名、Cookie+a1绑定、浏览器指纹检测、请求频率限制、媒体URL 30秒过期
- 已有成熟Python库 `xhs`（ReaJason/xhs）封装了API调用和签名，但内置签名易失效，需配合Playwright签名服务
- 用户选择"浏览器插件获取Cookie"方式，实际实现为：用户在浏览器登录小红书后，通过Cookie导出工具获取完整Cookie字符串，粘贴到前端输入框

---

## 项目文件结构

```
xhs-scraper/
├── start.bat                 # 一键启动脚本（英文内容）
├── requirements.txt          # Python依赖
├── stealth.min.js           # Playwright反检测脚本
├── sign_server.py           # Flask签名服务（端口5005）
├── app.py                   # FastAPI主服务（端口8000）
├── scraper/
│   ├── __init__.py
│   ├── client.py            # XhsClient封装+签名服务调用
│   ├── downloader.py        # 图片/视频下载器
│   ├── packager.py          # ZIP打包器
│   └── analyzer.py          # 数据分析（分词/情感/统计）
└── static/
    └── index.html           # 前端单页应用
```

---

## 技术栈

### 后端
- **FastAPI** — 主代理服务器，提供REST API
- **Flask + gevent** — 签名服务（Playwright浏览器自动化获取X-s签名）
- **xhs** — 小红书API客户端库（pip install xhs）
- **Playwright** — 无头浏览器，用于签名获取
- **jieba** — 中文分词
- **snownlp** — 中文情感分析

### 前端（CDN引入）
- **Chart.js 4.x** — 统计图表（柱状图、饼图、折线图）
- **wordcloud2.js** — 词云渲染
- **FileSaver.js** — 文件下载

---

## 后端API契约

| 方法 | 端点 | 请求 | 响应 | 说明 |
|------|------|------|------|------|
| POST | `/api/cookie` | `{cookie: "..."}` | `{status, message}` | 设置Cookie并验证 |
| POST | `/api/search` | `{keyword, page, page_size, sort}` | `{has_more, items: [NoteItem]}` | 关键词搜索笔记 |
| POST | `/api/search/user` | `{keyword, page, page_size}` | `{users: [UserItem]}` | 搜索用户 |
| GET | `/api/user/{user_id}/notes` | `?cursor=&num=30` | `{has_more, cursor, notes}` | 获取用户全部笔记 |
| GET | `/api/note/{note_id}` | `?xsec_token=...` | `NoteDetail` | 笔记详情（含媒体URL） |
| GET | `/api/note/{note_id}/comments` | `?cursor=&xsec_token=...` | `{has_more, cursor, comments}` | 笔记评论 |
| GET | `/api/note/{note_id}/sub_comments` | `?root_comment_id=...&cursor=` | `{has_more, cursor, comments}` | 子评论/回复 |
| POST | `/api/download/note/{note_id}` | `{xsec_token, with_comments}` | ZIP文件流 | 下载单篇笔记ZIP |
| POST | `/api/download/batch` | `{notes: [{note_id, xsec_token}]}` | ZIP文件流 | 批量下载 |
| POST | `/api/analyze` | `{notes: [NoteDetail]}` | `AnalysisResult` | 数据分析 |

---

## 实现步骤

### 阶段1：项目初始化与基础设施

#### 步骤1：创建项目结构和依赖文件
- 创建 `xhs-scraper/` 目录及子目录 `scraper/`、`static/`、`temp/`
- 编写 `requirements.txt`：fastapi, uvicorn, python-multipart, xhs, flask, gevent, playwright, jieba, snownlp, requests
- 下载 `stealth.min.js` 反检测脚本

#### 步骤2：实现签名服务 `sign_server.py`
- Flask应用，端口5005
- 启动时用Playwright打开小红书页面，加载stealth.min.js绕过检测
- 提供 `POST /sign` 端点：接收uri+data，在浏览器内执行 `window._webmsxyw()` 获取X-s/X-t签名
- 提供 `GET /a1` 端点：返回浏览器中的a1 Cookie值
- 签名服务独立进程运行，与主服务解耦

#### 步骤3：实现客户端管理 `scraper/client.py`
- `ClientManager` 类：按Cookie中的a1值管理XhsClient单例
- `_sign()` 函数：调用签名服务HTTP接口获取签名，支持3次重试
- 签名服务不可用时降级使用xhs内置签名

### 阶段2：主服务核心API

#### 步骤4：实现FastAPI主服务骨架 `app.py`
- 初始化FastAPI应用，添加CORS中间件（允许前端跨域）
- 添加速率限制中间件（API请求最小间隔2秒）
- 挂载静态文件目录 `static/`
- 全局异常处理器：IPBlockError(429)、NeedVerifyError(403)、SignError(401)

#### 步骤5：实现Cookie管理端点
- `POST /api/cookie`：接收Cookie字符串，创建XhsClient，调用 `get_self_info()` 验证有效性
- 全局变量存储当前Cookie

#### 步骤6：实现搜索API
- `POST /api/search`：调用 `client.get_note_by_keyword()`，支持排序（general/popularity/latest）
- `POST /api/search/user`：调用 `client.get_user_by_keyword()`
- `GET /api/user/{user_id}/notes`：调用 `client.get_user_notes()`，支持cursor分页循环获取全量

#### 步骤7：实现笔记详情和评论API
- `GET /api/note/{note_id}`：调用 `client.get_note_by_id()`，立即提取图片/视频URL（30秒过期）
- `GET /api/note/{note_id}/comments`：调用 `client.get_note_comments()`，递归获取子评论
- `GET /api/note/{note_id}/sub_comments`：调用 `client.get_note_sub_comments()`

### 阶段3：下载与打包

#### 步骤8：实现媒体下载器 `scraper/downloader.py`
- `MediaDownloader` 类：下载图片列表和视频
- 带重试机制（最多3次）、超时控制（图片15s、视频60s）
- 下载间隔0.3秒避免触发限制

#### 步骤9：实现ZIP打包器 `scraper/packager.py`
- `NotePackager` 类：将笔记打包为ZIP字节流
- ZIP结构：`笔记标题/note_info.json`（元数据）+ `content.txt`（正文）+ `images/`（图片）+ `video.mp4`（视频）+ `comments.json`（评论）
- 文件名清理（去除非法字符）

#### 步骤10：实现下载API端点
- `POST /api/download/note/{note_id}`：获取详情→下载媒体→获取评论→打包ZIP→返回文件流
- `POST /api/download/batch`：循环处理每篇笔记，打包为大ZIP返回
- 使用 `StreamingResponse` 流式返回

### 阶段4：数据分析

#### 步骤11：实现数据分析模块 `scraper/analyzer.py`
- **基础统计**：总笔记数、总点赞/收藏/评论、平均值
- **词频分析**：jieba分词 + 停用词过滤 + Counter统计TOP100词频
- **时间趋势**：按月聚合笔记数量和点赞数
- **情感分析**：snownlp对每篇笔记标题+描述打分，统计正面/中性/负面比例

#### 步骤12：实现分析API端点
- `POST /api/analyze`：接收笔记详情列表，返回完整分析结果

### 阶段5：前端HTML应用

#### 步骤13：实现前端基础布局 `static/index.html`
- **设计风格**：小红书品牌色调（红色#FF2442为主色），现代卡片式布局，毛玻璃效果
- **Cookie设置区**：输入框+设置按钮+状态指示灯
- **搜索区**：关键词搜索框+作者搜索框+排序切换（发布时间升序/降序）
- **操作栏**：下载全部按钮+数据分析按钮
- **结果表格**：封面缩略图、标题、作者、发布时间、点赞、收藏、评论数、下载按钮
- 使用CSS变量统一主题色，响应式布局

#### 步骤14：实现搜索与数据展示交互
- 关键词搜索：调用 `/api/search`，支持分页加载更多
- 作者搜索：先调用 `/api/search/user` 获取用户ID，再循环调用 `/api/user/{user_id}/notes` 获取全量笔记
- 搜索结果按发布时间排序（升序/降序切换）
- 加载状态提示、错误提示

#### 步骤15：实现下载功能
- 单篇下载：调用 `/api/download/note/{note_id}`，使用FileSaver.js保存ZIP
- 批量下载：调用 `/api/download/batch`，显示下载进度
- 下载按钮带loading状态

#### 步骤16：实现数据分析面板
- 模态框/侧边栏展示，四个Tab页：
  1. **基础统计**：数字卡片展示总笔记/点赞/收藏/评论及平均值
  2. **互动分析**：Chart.js柱状图（TOP10笔记互动数据对比）+ 饼图（情感分布）
  3. **词云与关键词**：wordcloud2.js词云 + TOP20关键词列表
  4. **时间趋势**：Chart.js双轴折线图（月度笔记数量+点赞趋势）

### 阶段6：启动脚本与集成

#### 步骤17：编写 `start.bat`
- 检查Python环境
- 自动安装依赖（pip install -r requirements.txt）
- 检查/下载 stealth.min.js
- 检查/安装 Playwright浏览器
- 后台启动签名服务（等待8秒初始化）
- 启动FastAPI主服务
- 自动打开浏览器访问 http://localhost:8000
- BAT文件内容全部使用英文

---

## 关键技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 签名方案 | Playwright浏览器自动化 | 无需逆向X-s算法，浏览器自动处理Cookie和指纹 |
| API客户端 | xhs库（ReaJason/xhs） | 纯Python，API封装完善，支持外部签名注入 |
| Cookie获取 | 用户手动粘贴 | 最简单可靠，避免浏览器插件开发复杂度 |
| 媒体下载 | 后端即时下载 | URL 30秒过期，必须在获取后立即下载 |
| 前端框架 | 原生HTML/CSS/JS | 单文件部署，无需构建工具 |
| 数据分析 | jieba + snownlp | 成熟的中文NLP库，轻量级 |

## 反反爬措施

1. **Playwright + stealth.min.js**：绕过浏览器指纹检测（Canvas/WebGL/字体指纹）
2. **真实浏览器签名**：在真实浏览器环境中获取X-s/X-t签名
3. **请求速率控制**：API请求最小间隔2秒，模拟真人操作
4. **Cookie管理**：支持用户更新Cookie，自动检测过期
5. **错误恢复**：IP封禁(429)、验证码(403)、签名错误(401)均有友好提示
6. **User-Agent一致性**：所有请求使用统一UA

## 验证步骤

1. 启动签名服务，用curl测试 `/sign` 和 `/a1` 端点
2. 启动主服务，设置Cookie后验证连接状态
3. 关键词搜索测试：搜索一个热门关键词，验证返回数据结构
4. 作者搜索测试：搜索一个用户名，验证能获取其全部笔记
5. 笔记详情测试：获取一篇笔记详情，验证图片/视频URL正确提取
6. 下载测试：下载单篇笔记ZIP，验证内容完整（元数据+正文+图片+评论）
7. 批量下载测试：下载多篇笔记，验证ZIP结构正确
8. 数据分析测试：对搜索结果执行分析，验证四项分析结果正确
9. 排序测试：切换升序/降序，验证表格排序正确
10. BAT脚本测试：双击start.bat，验证一键启动成功
