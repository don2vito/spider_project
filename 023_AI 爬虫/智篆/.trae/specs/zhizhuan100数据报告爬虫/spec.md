# zhizhuan100 数据报告爬虫与展示系统 Spec

## Why
zhizhuan100.com.cn 是智篆商业公司的数据分析网站，其 `/analysis` 页面展示大量行业趋势白皮书和数据报告。用户需要一个自动化工具来批量抓取这些报告数据（标题、链接、封面图片），并通过一个本地 HTML 应用进行浏览和下载，以便离线使用。

## What Changes
- 开发一个 Python 代理服务器，负责抓取 zhizhuan100.com.cn/analysis 全部5页数据报告
- 实现三层爬取策略（API 接口 → HTML 解析 → Browser Use 兜底）
- 开发一个 HTML 前端应用，展示报告表格（封面图片、报告名称），支持单个/批量/全量下载
- 生成 .bat 一键启动文件
- 生成 PRD 文档和 UI 方案文档（Word 格式）

## Impact
- Affected specs: 无（新建功能）
- Affected code: 新建 Python 爬虫服务器、HTML 前端应用、.bat 启动脚本、Word 文档

---

## ADDED Requirements

### Requirement: 网页数据抓取服务
系统 SHALL 提供一个 Python 后端服务，抓取 `https://zhizhuan100.com.cn/analysis` 的全量数据报告信息。

#### Scenario: 成功抓取全量数据
- **WHEN** 代理服务器启动并请求 `/api/reports` 接口
- **THEN** 返回包含所有页面报告的 JSON 数据（标题、链接、封面图片 URL）
- **AND** 数据去重（基于报告链接唯一标识）

#### Scenario: 三层爬取策略
- **WHEN** 第一层（API 接口拦截）成功
- **THEN** 直接使用 API 返回的 JSON 数据
- **WHEN** 第一层失败，第二层（HTML 解析）成功
- **THEN** 使用 BeautifulSoup 解析 HTML DOM 提取数据
- **WHEN** 前两层均失败，第三层（Browser Use）生效
- **THEN** 使用 Playwright 控制真实浏览器获取数据

### Requirement: 前端数据展示
系统 SHALL 提供一个 HTML 前端页面，展示全量报告数据。

#### Scenario: 展示报告表格
- **WHEN** 用户打开 HTML 页面
- **THEN** 自动从代理服务器获取数据并展示表格
- **AND** 表格包含：封面图片（缩略图）、报告名称、操作按钮

#### Scenario: 报告封面图片展示
- **WHEN** 表格加载完成
- **THEN** 每行显示报告的封面图片（缩略展示）

### Requirement: 报告下载功能
系统 SHALL 提供单个、批量和全量下载功能。

#### Scenario: 单个报告下载
- **WHEN** 用户点击某条报告的"下载"按钮
- **THEN** 下载该报告的详情页面所有图片（报告内容）

#### Scenario: 批量/全量下载
- **WHEN** 用户勾选多条报告并点击"批量下载"或点击"全量下载"
- **THEN** 将所选报告打包为 ZIP 文件下载

### Requirement: 一键启动
系统 SHALL 提供 .bat 文件实现一键启动。

#### Scenario: 启动代理服务器和前端
- **WHEN** 用户双击 .bat 文件
- **THEN** 自动启动 Python 代理服务器
- **AND** 自动在默认浏览器中打开前端页面
- **AND** .bat 文件与 Python 代码、HTML 文件在同一文件夹下
- **AND** .bat 文件内容使用英文

### Requirement: 文档输出
系统 SHALL 生成 PRD 文档和 UI 方案文档（Word 格式）。

#### Scenario: 生成 PRD 文档
- **WHEN** 开发完成
- **THEN** 输出完整的 PRD 文档（.docx 格式）

#### Scenario: 生成 UI 方案文档
- **WHEN** 开发完成
- **THEN** 输出完整的 UI 方案文档（.docx 格式）

---

## Technical Context

### 目标网站结构分析
- 建站平台：wezhan（CDN 加速），HTML 仅 925 字节，内容通过 CDN 加载的 Body.js 用 `document.write()` 注入
- 列表页 URL：`https://zhizhuan100.com.cn/analysis?page={N}`（共 5 页，每页 20 条，总计约 94 条）
- 每条报告包含：标题（h5 标签文本）、详情链接（`/productinfo/{id}.html?templateId=1647211`）、封面图片
- 详情页包含：报告标题 + 多张报告内容图片
- 图片域名：`img.wanwang.xin` / `aka.doubaocdn.com`

### 隐藏 API 发现（关键）
- **API 端点**: `POST https://zhizhuan100.com.cn/Designer/Common/GetData`
- **请求参数** (form-urlencoded):
  ```
  dataType=product&key=&pageIndex={N}&pageSize=20&selectCategory=889154
  &selectId=&dateFormater=yyyy-MM-dd&orderByField=createtime&orderByType=desc
  &templateId=1647211&postData=&es=false&setTop=true
  &__RequestVerificationToken={token}
  ```
- **响应格式** JSON:
  ```json
  {"IsSuccess": true, "Data": [{"Id": 3397502, "Name": "...", "PicUrl": "//img.wanwang.xin/...", "LinkUrl": "/productinfo/3397502.html?templateId=1647211", ...}]}
  ```
- 分页: `pageIndex=0` 对应第 2 页（点击 page 2 时发送），共 5 页，每页 20 条
- 需要 `__RequestVerificationToken` 防伪令牌（从页面 HTML 中提取）

### 分页机制
- jqPaginator jQuery 分页插件
- 分页按钮选择器: `li[jp-role='page'][jp-data='{N}'] a`
- 点击分页按钮触发 AJAX POST 请求到 `/Designer/Common/GetData`

### 技术栈
- Python 3（爬虫服务器 + Flask）
- requests + BeautifulSoup（HTML 解析）
- Playwright（Browser Use 兜底）
- HTML + CSS + JavaScript（前端应用）
- python-docx（生成 Word 文档）
