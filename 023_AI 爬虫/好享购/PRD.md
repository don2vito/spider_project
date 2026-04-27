# PRD: 好享购节目表 - 实时数据看板

> **文档版本**: v1.0
> **创建日期**: 2026-04-24
> **目标读者**: AI 编程工具（Cursor / Trae）
> **项目类型**: 单页面 HTML 应用 + Python 本地代理服务器

---

## 1. 项目概述

### 1.1 项目背景

好享购（hao24.com）是一家电视购物直播平台，每日发布直播节目单。用户需要手动浏览网站查看节目安排，效率低下。本项目旨在构建一个本地数据看板，自动抓取并展示好享购每日直播节目表，支持多天预览、区域切换和 Excel 导出。

### 1.2 项目目标

- 自动化抓取好享购直播节目表数据，免去手动浏览
- 以现代化深色主题看板形式展示节目信息（含商品图片、价格、状态等）
- 支持省内/省外区域切换和 3/7/14/30 天天数选择
- 提供一键 Excel 导出功能
- 桌面端与移动端均提供良好体验

### 1.3 技术选型

| 层级 | 技术方案 | 说明 |
|------|---------|------|
| 前端 | 单文件 HTML（内联 CSS + JS） | 零构建、零框架依赖，直接浏览器打开 |
| 后端 | Python HTTP 代理服务器（`server.py`） | 基于 `http.server`，使用 `requests` 库转发 API 请求，解决 CORS 限制 |
| 外部 CDN | Google Fonts (Noto Sans SC)、SheetJS (xlsx) | 字体与 Excel 导出 |
| 启动方式 | Windows 批处理脚本（`启动.bat`） | 一键启动代理服务器并打开浏览器 |

---

## 2. 用户故事

### US-01: 查看节目表
> 作为用户，我希望打开页面后自动加载并展示最近 7 天的直播节目表，这样我无需手动操作即可快速浏览节目安排。

**验收标准**:
- 页面加载后自动触发数据抓取
- 默认展示最近 7 天、省内区域的节目数据
- 数据按日期升序排列，同日期节目按时间排列
- 表格包含：日期、时间、状态、商品图片、商品名称、销售价、市场价、优惠、已售、编号

### US-02: 切换区域
> 作为用户，我希望能在"省内（江苏）"和"省外"之间切换，这样我可以查看不同区域的节目安排。

**验收标准**:
- 控制面板提供区域切换按钮组
- 切换区域后，下次抓取使用新区域参数
- 当前选中区域有明确的视觉高亮状态

### US-03: 选择天数范围
> 作为用户，我希望选择查看 3 天、7 天、14 天或 30 天的节目数据，这样我可以灵活控制数据范围。

**验收标准**:
- 控制面板提供天数选择按钮组（3/7/14/30）
- 默认选中 7 天
- 切换天数后，下次抓取使用新天数参数

### US-04: 导出 Excel
> 作为用户，我希望将当前节目数据导出为 Excel 文件，这样我可以离线查看或分享给他人。

**验收标准**:
- 提供"下载 Excel"按钮，仅在数据加载成功后可用
- 导出文件名格式：`快乐购节目表_YYYYMMDD.xlsx`
- Excel 包含表头行和所有节目数据行
- 列宽根据内容合理设置

### US-05: 查看直播状态
> 作为用户，我希望直观地看到每个节目的直播状态（正在直播/即将开播/已结束），这样我可以快速定位感兴趣的节目。

**验收标准**:
- 状态以彩色标签形式展示：正在直播（薄荷绿 + 脉冲动效）、即将开播（黄色）、已结束（灰色）
- "正在直播"状态有脉冲动画提示

### US-06: 移动端适配
> 作为用户，我希望在手机上也能方便地查看节目表，这样我随时随地都能获取节目信息。

**验收标准**:
- 768px 以下自动切换为卡片布局
- 卡片展示：商品图片、名称、时间、状态、价格
- 按日期分组，每组有日期标题
- 控制面板和统计卡片在移动端自适应

---

## 3. 功能需求

### 3.1 数据抓取模块

#### 3.1.1 API 请求

- **目标 URL**: `POST https://m.hao24.com/live/list.do`
- **请求体格式**: JSON
  ```json
  {
    "date": "YYYYMMDD",
    "areaCd": "02"
  }
  ```
- **区域编码**: `"02"` = 省内（江苏），`"03"` = 省外
- **请求间隔**: 每次请求间隔 400ms，避免频繁请求
- **失败重试**: 单次请求最多重试 3 次，重试间隔 1500ms
- **请求超时**: 15 秒

#### 3.1.2 代理策略

采用多级代理降级策略，按优先级依次尝试：

1. **本地代理**（优先）: `POST /api/proxy` -- 由 `server.py` 提供
   - 请求体: `{"targetUrl": "https://m.hao24.com/live/list.do", "method": "POST", "body": {"date":"YYYYMMDD","areaCd":"02"}}`
   - 本地代理将请求转发到目标 API，附加必要的请求头（User-Agent、Origin、Referer 等）

2. **CORS 公共代理**（降级）:
   - `https://corsproxy.io/?url=`
   - `https://proxy.killcors.com/?url=`
   - `https://api.cors.lol/?url=`

当所有代理均不可用时，显示错误提示："所有代理均不可用，请确保已启动 server.py 或检查网络"。

#### 3.1.3 进度反馈

- 抓取过程中显示进度条，格式：`正在抓取 YYYYMMDD（当前/总数）`
- 进度条使用品牌色到薄荷绿的渐变填充
- 抓取完成后进度条隐藏

### 3.2 数据解析模块

#### 3.2.1 API 响应结构

```json
{
  "state": true,
  "livelist": [
    {
      "liveGoods": {
        "goodsNm": "商品名称",
        "salePrc": "299.00",
        "imgUrl": "https://...",
        "beTime": "10:00-12:00",
        "status": "0",
        "payTips": "满减优惠",
        "goodsSn": "H001",
        "marketPrc": "599.00",
        "saleQty": "1234"
      }
    }
  ]
}
```

#### 3.2.2 数据映射

| API 字段 | 内部字段 | 表格列名 | 类型 | 说明 |
|----------|---------|---------|------|------|
| `date`（请求参数） | `date` | 日期 | string | YYYYMMDD 格式，前端格式化为 `MM-DD 周X` |
| `beTime` | `time` | 时间 | string | 直播时间段，如 `10:00-12:00` |
| `status` | `status` | 状态 | string | 状态码映射见下表 |
| `imgUrl` | `imageUrl` | 商品图片 | string | 图片 URL，用于缩略图展示 |
| `goodsNm` | `name` | 商品名称 | string | 最大宽度 220px，溢出省略号 |
| `salePrc` | `price` / `priceFormatted` | 销售价 | number / string | 解析为数字，格式化为 `¥xxx.xx` |
| `marketPrc` | `marketPrice` | 市场价 | string | 灰色删除线展示，前缀 `¥` |
| `payTips` | `payTips` | 优惠 | string | 黄色标签展示 |
| `saleQty` | `saleQty` | 已售 | string | 数字展示 |
| `goodsSn` | `sn` | 编号 | string | 灰色文字 |

#### 3.2.3 状态码映射

| status 值 | 显示文本 | CSS 类名 | 颜色 |
|-----------|---------|---------|------|
| `0` | 正在直播 | `live` | 薄荷绿 `#00d4aa` |
| `1` | 即将开播 | `upcoming` | 黄色 `#fbbf24` |
| `2` | 已结束 | `ended` | 灰色 `#6b7280` |
| `-1` | 其他 | `other` | 浅灰 `#9ca3af` |
| `-2` | 已结束 | `ended` | 灰色 `#6b7280` |

### 3.3 UI 渲染模块

#### 3.3.1 页面布局结构

```
+------------------------------------------+
|              Header（标题区）               |
|         好享购节目表 / HAPPIGO LIVE        |
+------------------------------------------+
|           Control Panel（控制面板）          |
|  [区域: 省内 | 省外]  [天数: 3|7|14|30]    |
|  [开始抓取]                  [下载 Excel]   |
+------------------------------------------+
|           Progress Bar（进度条）             |
+------------------------------------------+
|           Stats Cards（统计卡片）           |
|  [抓取天数]  [节目总数]  [正在直播]          |
+------------------------------------------+
|           Data Table（数据表格）             |
|  日期 | 时间 | 状态 | 图片 | 名称 | ...    |
|  ...（按日期升序，同日期首行有分隔线）        |
+------------------------------------------+
|              Footer（页脚）                 |
|        HAPPIGO PROGRAM SCHEDULE            |
+------------------------------------------+
```

#### 3.3.2 表格渲染规则

- 数据按日期升序排列
- 同一日期的首行在第一列上方显示 2px 品牌色分隔线（`data-date-first` 属性）
- 每行都有日期列，不合并单元格
- 日期列格式：`MM-DD` + 小字 `周X`
- 行入场动画：`fadeInUp`，延迟递增（每行 30ms，最大 800ms）

#### 3.3.3 商品图片处理

- 桌面端：56x56px 缩略图，圆角 8px，`object-fit: cover`
- 鼠标悬停：放大至 2.2 倍，带阴影，z-index 提升
- 移动端卡片：72x72px 缩略图
- 懒加载：所有图片使用 `loading="lazy"`
- 加载失败：桌面端显示占位符 `📦`，移动端隐藏图片元素

#### 3.3.4 移动端卡片布局

- 768px 以下自动切换（`.table-scroll` 隐藏，`.mobile-cards` 显示）
- 按日期分组，每组有粘性日期标题（`date-group-title`）
- 每张卡片：左侧商品图片 + 右侧信息区（名称、时间、状态标签、价格）
- 卡片入场动画延迟：每张 20ms，最大 600ms

### 3.4 Excel 导出模块

- 依赖 SheetJS CDN：`https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js`
- 导出列：日期、时间段、商品名称、商品编号、销售价格、市场价、支付优惠、已售数量、直播状态、商品图片URL
- 列宽设置：日期 12、时间段 12、商品名称 32、编号 12、销售价 10、市场价 10、优惠 18、已售 8、状态 10、图片URL 50
- Sheet 名称：`节目表`
- 文件名：`快乐购节目表_YYYYMMDD.xlsx`
- 导出前检查：数据为空时提示"暂无数据可导出"；XLSX 库未加载时提示"Excel 导出库加载失败"

### 3.5 统计展示模块

三张统计卡片：

| 卡片 | 数据来源 | 颜色 |
|------|---------|------|
| 抓取天数 | 去重后的日期数量 | 品牌色 `#ff6b35` |
| 节目总数 | 所有节目记录数 | 主文字色 `#e8e8ed` |
| 正在直播 | status === '0' 的记录数 | 薄荷绿 `#00d4aa` |

### 3.6 消息提示模块

- Toast 通知，固定在右上角，3 秒后自动消失
- 三种类型：`success`（薄荷绿）、`error`（红色）、`info`（品牌色）
- 入场动画：`slideInRight`
- 退场：透明度渐变 + 右移

---

## 4. 数据模型

### 4.1 Program 对象（前端内部数据结构）

```typescript
interface Program {
  date: string;           // YYYYMMDD 格式日期
  time: string;           // 直播时间段，如 "10:00-12:00"
  name: string;           // 商品名称
  sn: string;             // 商品编号
  price: number;          // 销售价（数值）
  priceFormatted: string; // 格式化后的销售价，如 "¥299.00" 或 "价格待定"
  marketPrice: string;    // 市场价（原始字符串）
  payTips: string;        // 优惠信息
  saleQty: string;        // 已售数量
  status: string;         // 状态码（字符串）
  statusText: string;     // 状态显示文本
  statusCls: string;      // 状态 CSS 类名
  imageUrl: string;       // 商品图片 URL
}
```

### 4.2 全局状态

```typescript
let allPrograms: Program[] = [];  // 当前加载的所有节目数据
let currentArea: string = '02';   // 当前选中区域编码
let currentDays: number = 7;      // 当前选中天数
let isFetching: boolean = false;  // 是否正在抓取中（防重复提交）
```

---

## 5. API 接口规范

### 5.1 上游 API：好享购节目表接口

| 属性 | 值 |
|------|---|
| URL | `https://m.hao24.com/live/list.do` |
| Method | `POST` |
| Content-Type | `application/json; charset=utf-8` |

**请求体**:

```json
{
  "date": "20260424",
  "areaCd": "02"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `date` | string | 是 | 查询日期，YYYYMMDD 格式 |
| `areaCd` | string | 是 | 区域编码：`02`=省内（江苏），`03`=省外 |

**成功响应**:

```json
{
  "state": true,
  "livelist": [
    {
      "liveGoods": {
        "goodsNm": "商品名称",
        "salePrc": "299.00",
        "imgUrl": "https://img.hao24.com/xxx.jpg",
        "beTime": "10:00-12:00",
        "status": "0",
        "payTips": "满200减50",
        "goodsSn": "H00012345",
        "marketPrc": "599.00",
        "saleQty": "1234"
      }
    }
  ]
}
```

**响应字段说明**:

| 字段路径 | 类型 | 说明 |
|---------|------|------|
| `state` | boolean | 请求是否成功，`true`=成功 |
| `livelist` | array | 节目列表 |
| `livelist[].liveGoods` | object | 商品详情对象 |
| `livelist[].liveGoods.goodsNm` | string | 商品名称 |
| `livelist[].liveGoods.salePrc` | string | 销售价格（字符串形式的数字） |
| `livelist[].liveGoods.imgUrl` | string | 商品图片 URL |
| `livelist[].liveGoods.beTime` | string | 直播时间段 |
| `livelist[].liveGoods.status` | string | 直播状态码 |
| `livelist[].liveGoods.payTips` | string | 支付优惠信息 |
| `livelist[].liveGoods.goodsSn` | string | 商品编号 |
| `livelist[].liveGoods.marketPrc` | string | 市场价格 |
| `livelist[].liveGoods.saleQty` | string | 已售数量 |

### 5.2 本地代理 API

| 属性 | 值 |
|------|---|
| URL | `POST http://localhost:8080/api/proxy` |
| Method | `POST` |
| Content-Type | `application/json` |

**请求体**:

```json
{
  "targetUrl": "https://m.hao24.com/live/list.do",
  "method": "POST",
  "body": {
    "date": "20260424",
    "areaCd": "02"
  }
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `targetUrl` | string | 是 | 目标 API 的完整 URL |
| `method` | string | 否 | HTTP 方法，默认 `POST` |
| `body` | object/string/bytes | 否 | 转发到目标 API 的请求体 |

**代理服务器行为**:
- 接收前端请求后，附加预设的请求头（模拟移动端浏览器），转发到 `targetUrl`
- 预设请求头包括：User-Agent（Android Chrome）、Accept、Accept-Language、Content-Type、Origin（`https://m.hao24.com`）、Referer（`https://m.hao24.com/live/today.html`）、X-Requested-With
- 请求超时：15 秒
- 响应头添加 `Access-Control-Allow-Origin: *`
- 支持 `OPTIONS` 预检请求

**错误响应**:

```json
// 400 - 缺少 targetUrl
{"error": "缺少 targetUrl"}

// 502 - 上游 HTTP 错误
{"error": "HTTP 403", "detail": "..."}

// 500 - 服务器内部错误
{"error": "Connection timeout"}
```

### 5.3 静态文件服务

代理服务器同时作为静态文件服务器，支持直接访问 `happigo.html`：

- 访问地址：`http://localhost:8080/happigo.html`
- 默认端口：8080，可通过 `--port` 参数指定
- 工作目录：`server.py` 所在目录

---

## 6. 非功能需求

### 6.1 性能要求

| 指标 | 要求 |
|------|------|
| 请求间隔 | 相邻两次 API 请求之间至少间隔 400ms |
| 请求超时 | 单次请求 15 秒超时 |
| 重试策略 | 失败后最多重试 3 次，重试间隔 1500ms |
| 图片懒加载 | 所有商品图片使用 `loading="lazy"` 原生懒加载 |
| 动画性能 | 使用 CSS transform/opacity 动画，避免触发重排 |

### 6.2 容错与降级

- **代理降级**: 本地代理不可用时，自动尝试 CORS 公共代理列表
- **单日失败容忍**: 某一天的数据抓取失败不影响其他天，跳过并继续
- **图片加载失败**: 显示占位符图标，不中断页面渲染
- **XLSX 库加载失败**: 导出按钮点击时检测，提示用户刷新页面
- **防重复提交**: `isFetching` 标志位防止并发抓取

### 6.3 兼容性

- 现代浏览器（Chrome、Firefox、Safari、Edge 最新两个主版本）
- 移动端浏览器（iOS Safari、Android Chrome）
- Python 3.x 运行环境
- 依赖库：`requests`（Python）

### 6.4 安全性

- 本地代理仅绑定 `0.0.0.0`，不对外暴露
- 代理服务器无身份认证（仅限本地开发使用）
- 不存储任何用户数据，所有数据实时从 API 获取

---

## 7. 文件结构

```
project-root/
├── happigo.html      # 前端页面（单文件，约 1237 行）
│                      #   - 内联 CSS（约 689 行）
│                      #   - 内联 JavaScript（约 430 行）
│                      #   - HTML 结构（约 100 行）
├── server.py         # Python 本地代理服务器（约 136 行）
│                      #   - ProxyHandler 类（处理 API 代理 + 静态文件）
│                      #   - 命令行参数解析（--port）
└── 启动.bat           # Windows 一键启动脚本（约 27 行）
                       #   - 启动 server.py
                       #   - 等待 2 秒后打开浏览器
```

### 7.1 happigo.html 内部模块划分

| 模块 | 行范围 | 职责 |
|------|--------|------|
| Module A: Config & Constants | JS 起始 ~ 第 837 行 | 配置常量（API URL、代理列表、重试参数）、状态映射、全局变量 |
| Module B: Proxy Fetch | ~第 840 ~ 880 行 | 多级代理请求逻辑，依次尝试本地代理和 CORS 代理 |
| Module C: API Data Fetch | ~第 883 ~ 930 行 | 单日/批量节目数据抓取，含重试和进度回调 |
| Module D: Data Parse | ~第 933 ~ 964 行 | API 响应解析，映射为内部 Program 对象 |
| Module E: UI Rendering | ~第 967 ~ 1090 行 | 表格渲染、移动端卡片渲染、统计更新、进度条、Toast |
| Module F: Excel Export | ~第 1093 ~ 1138 行 | SheetJS 导出逻辑 |
| Module G: Init & Events | ~第 1141 ~ 1233 行 | 日期生成、事件绑定、页面加载自动抓取 |

### 7.2 server.py 内部结构

| 组件 | 说明 |
|------|------|
| `API_HEADERS` | 固定请求头字典，模拟移动端浏览器 |
| `ProxyHandler` | 继承 `SimpleHTTPRequestHandler`，处理 POST 代理和 OPTIONS 预检 |
| `handle_proxy()` | 解析请求体，转发到目标 URL，处理错误 |
| `do_OPTIONS()` | 处理 CORS 预检请求 |
| `send_json_response()` | 发送 JSON 响应的辅助方法 |
| `main()` | 命令行入口，启动 HTTP 服务器 |

---

## 8. UI 设计规范

### 8.1 设计风格

现代深色商务风格，以深色背景搭配高对比度的品牌色和状态色，营造专业数据看板氛围。

### 8.2 色彩系统

| 用途 | 变量名 | 色值 | 说明 |
|------|--------|------|------|
| 主背景 | `--bg-primary` | `#0a0a0f` | 页面底色 |
| 卡片背景 | `--bg-card` | `#12121a` | 卡片/面板背景 |
| 卡片悬停 | `--bg-card-hover` | `#1a1a28` | 鼠标悬停态 |
| 输入框背景 | `--bg-input` | `#0e0e16` | 输入控件底色 |
| 品牌色 | `--brand` | `#ff6b35` | 活力橙，主色调 |
| 品牌暗色 | `--brand-dim` | `#cc5529` | 渐变/按下态 |
| 品牌光晕 | `--brand-glow` | `rgba(255,107,53,0.25)` | 阴影/发光 |
| 直播状态 | `--live` | `#00d4aa` | 薄荷绿，直播中 |
| 直播光晕 | `--live-glow` | `rgba(0,212,170,0.3)` | 直播状态发光 |
| 即将开播 | `--upcoming` | `#fbbf24` | 黄色 |
| 已结束 | `--ended` | `#6b7280` | 灰色 |
| 主文字 | `--text-primary` | `#e8e8ed` | 标题/正文 |
| 次文字 | `--text-secondary` | `#8888a0` | 标签/辅助文字 |
| 弱文字 | `--text-muted` | `#55556a` | 占位/提示文字 |
| 边框 | `--border` | `#1e1e2e` | 默认边框 |
| 浅边框 | `--border-light` | `#2a2a3e` | 悬停边框 |

### 8.3 字体

- 主字体：`Noto Sans SC`（Google Fonts CDN）
- 字重使用：300（辅助）、400（正文）、500（标签）、700（强调）、900（标题）
- 回退字体：`-apple-system, BlinkMacSystemFont, sans-serif`

### 8.4 圆角与阴影

| 元素 | 圆角 | 阴影 |
|------|------|------|
| 小按钮/标签 | `6px` (`--radius-sm`) | 无 |
| 卡片/面板 | `10px` (`--radius`) | `0 4px 24px rgba(0,0,0,0.4)` |
| 大面板 | `16px` (`--radius-lg`) | 同上 |
| 品牌按钮 | `10px` | `0 4px 20px var(--brand-glow)` |

### 8.5 动效规范

| 动效名称 | CSS 关键帧 | 应用场景 | 参数 |
|---------|-----------|---------|------|
| fadeInDown | `translateY(-20px)` -> `translateY(0)` | Header 入场 | 0.6s ease-out |
| fadeInUp | `translateY(16px)` -> `translateY(0)` | 控制面板/表格行/卡片入场 | 0.4~0.6s ease-out |
| pulse | `opacity/scale` 循环 | 直播状态指示点 | 1.5s ease-in-out infinite |
| spin | `rotate(360deg)` | 加载旋转器 | 0.8s linear infinite |
| slideInRight | `translateX(40px)` -> `translateX(0)` | Toast 通知入场 | 0.3s ease-out |
| shimmer | `background-position` 平移 | 骨架屏加载效果 | 1.5s ease-in-out infinite |

### 8.6 背景氛围

页面背景使用 `body::before` 伪元素叠加两层径向渐变：
- 左上角：品牌色微光 `rgba(255,107,53,0.04)`
- 右下角：薄荷绿微光 `rgba(0,212,170,0.03)`
- 尺寸 200% x 200%，居中定位，`pointer-events: none`

### 8.7 标题渐变

Header 标题使用三色渐变文字：
- `linear-gradient(135deg, #ff6b35 0%, #ff9a6c 50%, #00d4aa 100%)`
- 通过 `background-clip: text` + `-webkit-text-fill-color: transparent` 实现

---

## 9. 技术约束

### 9.1 前端约束

- **单文件架构**: 所有 HTML、CSS、JavaScript 必须包含在 `happigo.html` 单个文件中，不得拆分
- **无构建工具**: 不使用 Webpack、Vite 等构建工具，不使用 npm
- **无框架依赖**: 不使用 React、Vue 等前端框架
- **CDN 依赖**:
  - Google Fonts: `https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900`
  - SheetJS: `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js`
- **浏览器 API**: 使用原生 `fetch` API，不引入 axios 等库
- **CSS 变量**: 所有设计 token 使用 CSS 自定义属性（`:root` 中定义）

### 9.2 后端约束

- **Python 标准库优先**: HTTP 服务器使用 `http.server` 标准库
- **唯一外部依赖**: `requests` 库（用于代理转发）
- **无 Web 框架**: 不使用 Flask、FastAPI 等
- **端口可配置**: 默认 8080，通过 `--port` / `-p` 命令行参数指定
- **无数据库**: 不持久化存储任何数据
- **无认证**: 仅限本地开发使用

### 9.3 部署约束

- **本地运行**: 项目设计为本地运行，不部署到公网服务器
- **启动方式**: Windows 用户双击 `启动.bat`；其他平台手动运行 `python server.py`
- **文件同目录**: `happigo.html`、`server.py`、`启动.bat` 必须位于同一目录

---

## 10. 交互流程

### 10.1 页面加载流程

```
页面加载
  |
  v
DOMContentLoaded 事件触发
  |
  v
绑定事件监听器（区域切换、天数选择、抓取按钮、导出按钮）
  |
  v
自动调用 startFetch()
  |
  v
生成日期列表（从今天往前推 currentDays 天）
  |
  v
逐天请求 API（间隔 400ms，失败重试 3 次）
  |  |
  |  v
  |  更新进度条
  |
  v
所有请求完成
  |
  v
解析数据 -> 渲染表格 + 卡片 -> 更新统计 -> 启用导出按钮
  |
  v
显示 Toast 通知（成功/失败）
```

### 10.2 用户操作流程

```
用户切换区域/天数
  |
  v
更新 currentArea / currentDays 变量
  |
  v
等待用户点击"开始抓取"（或"重新抓取"）
  |
  v
重复 10.1 的抓取流程
```

```
用户点击"下载 Excel"
  |
  v
检查 allPrograms 是否为空
  |
  v
检查 XLSX 库是否可用
  |
  v
构建工作表数据（含表头）
  |
  v
设置列宽 -> 生成文件 -> 触发下载
  |
  v
显示成功 Toast
```

---

## 11. 配置常量参考

以下为前端 JavaScript 中的核心配置，供开发时参考：

```javascript
const CONFIG = {
    API_URL: 'https://m.hao24.com/live/list.do',
    PROXY_LIST: [
        '/api/proxy',                          // 本地代理（优先）
        'https://corsproxy.io/?url=',          // CORS 代理 1
        'https://proxy.killcors.com/?url=',    // CORS 代理 2
        'https://api.cors.lol/?url='           // CORS 代理 3
    ],
    DEFAULT_DAYS: 7,
    MAX_RETRIES: 3,
    RETRY_DELAY: 1500,     // ms
    REQUEST_INTERVAL: 400,  // ms
    TIMEOUT: 15000,         // ms
};
```

以下为 Python 代理服务器的预设请求头：

```python
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G991B) ...',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Content-Type': 'application/json; charset=utf-8',
    'Origin': 'https://m.hao24.com',
    'Referer': 'https://m.hao24.com/live/today.html',
    'X-Requested-With': 'XMLHttpRequest',
}
```

---

## 附录 A：响应式断点

| 断点 | 变化 |
|------|------|
| `> 768px` | 桌面端：表格布局，完整控制面板 |
| `<= 768px` | 移动端：卡片布局，控制面板紧凑排列，按钮全宽 |
| `<= 480px` | 小屏：统计卡片单列堆叠 |

## 附录 B：Excel 导出列定义

| 列序 | 列名 | 数据源 | 宽度（字符数） |
|------|------|--------|--------------|
| A | 日期 | `p.date` | 12 |
| B | 时间段 | `p.time` | 12 |
| C | 商品名称 | `p.name` | 32 |
| D | 商品编号 | `p.sn` | 12 |
| E | 销售价格 | `p.priceFormatted` | 10 |
| F | 市场价 | `p.marketPrice`（前缀 `¥`） | 10 |
| G | 支付优惠 | `p.payTips` | 18 |
| H | 已售数量 | `p.saleQty` | 8 |
| I | 直播状态 | `p.statusText` | 10 |
| J | 商品图片URL | `p.imageUrl` | 50 |
