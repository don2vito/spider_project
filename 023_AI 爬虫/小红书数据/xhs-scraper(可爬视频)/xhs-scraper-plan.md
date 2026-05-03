# 小红书数据采集与分析系统 — 实施计划

## 一、任务重述

### 目标
构建一个完整的小红书数据采集与分析系统，包含三个核心文件：
1. **Python 代理服务器**（`server.py`）— 爬虫后端，具备反反爬能力
2. **HTML 前端应用**（`index.html`）— 搜索、展示、下载、分析
3. **一键启动脚本**（`start.bat`）— 启动代理服务器并打开前端页面

### 核心功能
- 输入作者ID → 搜索该作者主页所有笔记 → 展示全量数据
- 表格支持按发布时间自定义升降序排列
- 每条笔记提供下载按钮（ZIP打包：文本+图片+视频+评论）
- "下载全部"按钮（批量ZIP下载）
- "数据分析"按钮（综合分析报告：互动数据统计+内容趋势分析）
- 支持扫码/账号密码登录
- 反反爬措施（X-s签名、请求频率控制、错误重试）

### 输出格式
- `server.py`：Python FastAPI 后端
- `index.html`：单文件 HTML 前端（内嵌CSS/JS）
- `start.bat`：Windows 一键启动脚本（内容英文）

### 成功标准
- 三个文件放在同一文件夹下，双击 `start.bat` 即可启动系统
- 前端页面可正常搜索、展示、排序、下载、分析
- 爬虫具备基本的反反爬能力

---

## 二、当前状态分析

### 技术调研结论

#### 小红书 API 架构
- API 域名：`https://edith.xiaohongshu.com`
- 用户笔记列表：`GET /api/sns/web/v1/user_posted?user_id=xxx&num=30&cursor=xxx`
- 笔记详情：`POST /api/sns/web/v1/feed`（body: `{"source_note_id": "xxx"}`）
- 评论列表：`GET /api/sns/web/v2/comment/page?note_id=xxx&cursor=xxx`
- 评论回复：`GET /api/sns/web/v2/comment/sub/page?note_id=xxx&root_comment_id=xxx&cursor=xxx`
- 用户信息：`GET /api/sns/web/v1/user/otherinfo?user_id=xxx`

#### 反爬机制
- **X-s 签名**：核心防护，每次请求需动态生成
- **Cookie 验证**：`a1`（设备标识，参与签名）+ `web_session`（登录凭证）
- **频率限制**：单IP请求间隔建议 ≥ 2秒
- **IP 封锁**：频繁请求返回 403/445/446/448
- **验证码**：滑块/图形/旋转验证码

#### 签名方案
- 使用 `xhshow` 库（纯Python，MIT License，464 stars，持续更新至2025年）
- `pip install xhshow`
- API：`signer.sign_xs_get(uri, a1_value, params)` / `signer.sign_xs_post(uri, a1_value, payload)`

#### 前端技术选型
- 纯 HTML/CSS/JS 单文件（无框架依赖）
- 表格排序：sortable-tablesort（1.52KB CDN）
- 图表库：ECharts（CDN，中文文档完善，图表类型丰富）
- 小红书红色主题（#FF2442）

#### 后端技术选型
- FastAPI + Uvicorn（异步高性能）
- httpx（异步HTTP客户端）
- stream-zip（流式ZIP生成，内存高效）
- pandas + plotly（数据分析与图表生成）

---

## 三、详细实施计划

### 步骤 1：创建 `server.py` — Python 代理服务器

**文件**：`/workspace/server.py`

**架构设计**：
```
FastAPI (:8080)
├── 静态文件服务 → index.html
├── /api/login/qr         → 获取登录二维码
├── /api/login/check      → 轮询扫码状态
├── /api/login/password   → 账号密码登录
├── /api/session/status   → 检查登录状态
├── /api/session/set      → 手动设置Cookie
├── /api/search           → 搜索作者笔记（核心）
├── /api/note/detail      → 获取笔记详情
├── /api/note/comments    → 获取笔记评论
├── /api/download/:id     → 下载单条笔记ZIP
├── /api/download_all     → 批量下载ZIP
└── /api/analyze          → 数据分析
```

**核心模块**：

1. **XHSSigner 类** — X-s 签名封装
   - 使用 xhshow 库生成签名
   - 自动注入 x-s、x-t、x-s-common 请求头
   - 处理签名失败和过期

2. **SessionManager 类** — 登录态管理
   - Cookie 持久化（JSON文件）
   - 自动加载/保存 Cookie
   - 会话有效性验证
   - 支持手动设置 Cookie（从浏览器复制）

3. **XHSClient 类** — 小红书 API 客户端
   - 异步请求封装（httpx）
   - 自动签名注入
   - 请求频率控制（随机延迟 2-5秒）
   - 指数退避重试（最多3次）
   - 分页自动翻页（cursor 机制）

4. **DataAnalyzer 类** — 数据分析
   - 互动数据统计（点赞/收藏/评论 TOP10）
   - 发布时间趋势分析
   - 内容类型分布（图文 vs 视频）
   - 互动率排名
   - 发布频率分析
   - 输出 JSON 格式分析结果（前端用 ECharts 渲染）

5. **ZIPExporter 类** — ZIP 打包导出
   - 使用 stream-zip 流式生成
   - 包含：笔记文本（JSON）、图片文件、视频文件、评论数据（JSON）
   - 支持单条和批量下载

**反反爬措施**：
- X-s 签名（xhshow 库）
- 随机 User-Agent 轮换
- 请求间隔随机延迟（2-5秒，正态分布）
- 指数退避重试（失败后等待 5s/15s/45s）
- 完整的浏览器请求头模拟
- Cookie 自动管理

**关键依赖**：
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
httpx>=0.27.0
xhshow>=0.1.1
stream-zip>=0.0.71
pandas>=2.2.0
```

### 步骤 2：创建 `index.html` — 前端应用

**文件**：`/workspace/index.html`

**设计风格**：小红书红色主题
- 主色：#FF2442
- 背景：白色 + 浅灰
- 胶囊按钮、圆角卡片
- 字体：PingFang SC / Microsoft YaHei

**页面结构**：

```
┌─────────────────────────────────────────┐
│  🔴 小红书数据采集系统        [登录状态] │
├─────────────────────────────────────────┤
│  [作者ID输入框] [搜索按钮]              │
├─────────────────────────────────────────┤
│  [下载全部] [数据分析] [排序: ▼发布时间] │
├─────────────────────────────────────────┤
│  ┌──┬──────┬────┬────┬────┬────┬───┐  │
│  │序│ 封面 │标题│时间│点赞│收藏│操作│  │
│  ├──┼──────┼────┼────┼────┼────┼───┤  │
│  │1 │ img  │... │... │128│ 56 │[↓] │  │
│  │2 │ img  │... │... │256│120 │[↓] │  │
│  │..│      │    │    │    │    │    │  │
│  └──┴──────┴────┴────┴────┴────┴───┘  │
├─────────────────────────────────────────┤
│  [数据分析报告区域 - 默认隐藏]          │
│  ┌──────────┐ ┌──────────┐             │
│  │互动趋势图│ │内容分布图│             │
│  └──────────┘ └──────────┘             │
│  ┌──────────┐ ┌──────────┐             │
│  │TOP10排名 │ │发布频率图│             │
│  └──────────┘ └──────────┘             │
└─────────────────────────────────────────┘
```

**视图切换**：
1. **登录视图** — 扫码登录 + 账号密码登录（Tab切换）
2. **主视图** — 搜索 + 数据表格 + 操作按钮
3. **分析视图** — 数据分析报告（ECharts图表）

**核心功能实现**：
- 搜索表单：输入作者ID → 调用 `/api/search` → 渲染表格
- 表格排序：使用 sortable-tablesort 库，发布时间列使用 `data-sort` 时间戳
- 单条下载：调用 `/api/download/:id` → Blob → 触发下载
- 全部下载：调用 `/api/download_all` → 流式读取 → 进度条 → Blob下载
- 数据分析：调用 `/api/analyze` → 获取 JSON → ECharts 渲染图表
- 登录：扫码轮询 + 密码登录 → Cookie 管理
- Toast 通知：操作反馈
- 加载状态：Spinner + 进度条

**CDN 依赖**：
- sortable-tablesort（表格排序）
- ECharts（图表可视化）

### 步骤 3：创建 `start.bat` — 一键启动脚本

**文件**：`/workspace/start.bat`

**功能**：
1. 检查 Python 是否安装
2. 自动安装依赖（pip install）
3. 启动 FastAPI 服务器（后台运行）
4. 等待服务器就绪
5. 自动打开浏览器访问 `http://localhost:8080`

**内容使用英文**。

---

## 四、假设与决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 后端框架 | FastAPI | 异步高性能，内置CORS，自动文档 |
| 签名方案 | xhshow 库 | 纯Python，无需Node.js，维护活跃 |
| 前端方案 | 单文件HTML | 部署简单，双击即可使用 |
| 图表库 | ECharts | 中文文档完善，图表类型丰富 |
| ZIP方案 | stream-zip | 流式生成，内存高效 |
| 端口 | 8080 | 常用端口，不易冲突 |
| 数据存储 | 内存 + 临时文件 | 无需数据库，简化部署 |
| 登录方式 | Cookie 手动配置 + 扫码/密码 | 覆盖多种场景 |

---

## 五、验证步骤

1. **依赖安装验证**：`pip install fastapi uvicorn httpx xhshow stream-zip pandas` 成功
2. **服务器启动验证**：`python server.py` 无报错，访问 `http://localhost:8080` 返回前端页面
3. **登录功能验证**：设置Cookie后，`/api/session/status` 返回已登录状态
4. **搜索功能验证**：输入作者ID，表格正确展示笔记列表
5. **排序功能验证**：点击发布时间列头，表格按时间升降序排列
6. **单条下载验证**：点击下载按钮，ZIP包含文本+图片+评论
7. **全部下载验证**：点击下载全部，生成包含所有笔记的ZIP
8. **数据分析验证**：点击数据分析，展示互动趋势、内容分布等图表
9. **一键启动验证**：双击 `start.bat`，自动安装依赖、启动服务器、打开浏览器
10. **反反爬验证**：连续请求不触发封禁，签名正确生成

---

## 六、文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| server.py | /workspace/server.py | Python 代理服务器（后端） |
| index.html | /workspace/index.html | HTML 前端应用 |
| start.bat | /workspace/start.bat | 一键启动脚本 |
