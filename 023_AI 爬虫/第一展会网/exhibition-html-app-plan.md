# 展会信息爬虫 HTML 应用 - 实施计划

## 任务理解

**目标**：将 Python 爬虫逻辑移植为单个 HTML 文件应用，打开即可自动抓取 onezh.com 的 2026 年展会数据，展示在页面上，并支持下载 Excel。

**核心需求**：
1. 打开 HTML 自动抓取数据
2. 按日期升序排序
3. 表格带图片（展会封面图）
4. 区分上海/非上海
5. 提供下载 Excel 功能

---

## 关键技术约束（已验证）

### CORS 问题
- `onezh.com` **无** `Access-Control-Allow-Origin` 头，浏览器直接 fetch 会被 CORS 拦截
- `x-frame-options: sameorigin`，无法 iframe 嵌入
- **解决方案**：使用公共 CORS 代理 `https://api.codetabs.com/v1/proxy/?quest=` （已验证可用，返回 `access-control-allow-origin: *`，支持 GET，限速 5次/秒）
- **备用代理**：`https://corsproxy.io/?` （备选，以防 codetabs 不可用）

### Excel 导出
- 使用 **SheetJS** (`xlsx.full.min.js`) CDN 版本，纯浏览器端生成 `.xlsx` 文件
- CDN: `https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js`

### 图片处理
- 展会封面图 URL 来自 `onezh.com` 的 `<img>` 标签（`img.onezh.com` 域名）
- 图片本身无 CORS 限制（`<img>` 标签不受 CORS 约束），可直接在 `<img src>` 中使用
- 部分图片可能加载失败，需 `onerror` 回退处理

---

## 网站结构（从 Python 代码提取）

### URL 模式
```
/zhanhui/{page}_0_0_0_{YYYYMMDD}/{YYYYMMDD}/
```

### 12 个月日期
```
1月:  20260101 ~ 20260131    2月:  20260201 ~ 20260228
3月:  20260301 ~ 20260331    4月:  20260401 ~ 20260430
5月:  20260501 ~ 20260531    6月:  20260601 ~ 20260630
7月:  20260701 ~ 20260731    8月:  20260801 ~ 20260831
9月:  20260901 ~ 20260930    10月: 20261001 ~ 20261031
11月: 20261101 ~ 20261130    12月: 20261201 ~ 20261231
```

### HTML 解析逻辑
- 展会条目：`<div class='row'>` 中 `<strong><a>` 获取名称/链接
- 封面图：`<div class='row'>` 内第一个 `<img>` 的 `src`
- 展会时间：`<em class='cgree1'>` 中 `展会时间：...`
- 展馆名称：`<em class='cgree1'>` 中 `展馆：...`
- 面积/参商/观众：`<div class='area'>` / `<div class='people1'>` / `<div class='people2'>`
- 简介：第一个 `<em class='cgree1'>` 文本
- 分页：`<div class="NewPage">` 中 `共N页` 文本

### 上海判断
展馆名称包含"上海"即判定为上海展会

---

## 设计方案

### 视觉风格
- **方向**：现代数据仪表盘风格，深色主题 + 鲜明强调色
- **配色**：深灰底 (#0f1117) + 翡翠绿强调 (#10b981) + 暖橙辅助 (#f59e0b)
- **字体**：Noto Sans SC（中文）+ DM Sans（数字/英文）
- **布局**：顶部统计卡片 → Tab 切换（全部/上海/非上海）→ 数据表格 → 底部下载按钮

### 功能模块
1. **顶部状态栏**：显示抓取进度（当前月份/总月份数、已获取条数）
2. **统计卡片**：总数、上海展会数、非上海展会数、本月展会数
3. **Tab 切换**：全部 | 上海展会 | 非上海展会
4. **数据表格**：序号、封面图、展会名称、展会时间、展馆名称、面积、参商、观众、操作（详情链接）
5. **排序**：默认按展会开始日期升序
6. **下载按钮**：生成 Excel（两个 Sheet：上海/非上海）
7. **加载状态**：骨架屏 + 进度条

---

## 实施步骤

### Step 1: 创建 HTML 文件
- 文件：`/workspace/展会信息查询.html`
- 单文件，包含所有 HTML/CSS/JS
- CDN 依赖：SheetJS (xlsx)、Google Fonts (Noto Sans SC + DM Sans)

### Step 2: 实现爬虫逻辑（JS 移植）
- `fetchViaProxy(url)` — 通过 CORS 代理请求
- `parsePage(html)` — DOMParser 解析 HTML，提取展会数据
- `getTotalPages(html)` — 提取总页数
- `crawlMonth(monthConfig)` — 爬取单月所有页
- `crawlAll()` — 串行爬取 12 个月（带延迟）
- 请求间隔 200ms（代理限速 5次/秒）

### Step 3: 实现数据展示
- 解析完成后按日期升序排序
- 渲染统计卡片
- 渲染表格（带封面图缩略图）
- Tab 切换过滤

### Step 4: 实现 Excel 下载
- 使用 SheetJS 创建 Workbook
- 两个 Sheet：上海展会 / 非上海展会
- 列：月份、展会名称、展会时间、展馆名称、展会面积、参商数量、观众数量、展会简介、详情链接
- 调用 `XLSX.writeFile()` 触发下载

### Step 5: 验证
- 在浏览器中打开 HTML 文件
- 确认自动抓取、数据展示、图片加载、Excel 下载均正常

---

## 假设与决策
1. **CORS 代理**：使用 `api.codetabs.com`，备用 `corsproxy.io`
2. **请求速率**：200ms 间隔（代理限速 5次/秒，留余量）
3. **图片**：直接使用原始 URL，`onerror` 显示占位符
4. **排序**：从展会时间字符串中提取开始日期进行排序
5. **单文件**：所有代码在一个 HTML 文件中，无外部依赖文件
6. **无框架**：纯 HTML/CSS/JS，不使用 React/Vue（保持简洁）
