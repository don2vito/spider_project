# 好享购节目表 - UI 设计方案文档

> **项目名称**：好享购节目表 - 实时数据看板
> **文档版本**：v1.0
> **文档读者**：AI 编程工具（Cursor / Trae）
> **文档语言**：中文
> **设计风格**：深色主题 · 数据展示型 · 单页面应用（SPA）

---

## 一、设计理念

### 1.1 核心定位

好享购节目表是一个面向电视购物节目的**实时数据看板**，用户通过该页面查看节目排期、商品信息、价格与销售数据。页面以数据密度和可读性为核心，兼顾视觉美感与操作效率。

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **信息密度优先** | 表格展示为主，单屏呈现尽可能多的节目数据，减少翻页操作 |
| **深色护眼** | 近黑色背景降低长时间观看的视觉疲劳，适合长时间使用 |
| **品牌色引导** | 活力橙（#ff6b35）作为品牌色贯穿全页，薄荷绿（#00d4aa）标识直播状态，形成清晰的视觉层级 |
| **动效克制** | 仅在入场、状态切换、交互反馈时使用动效，不干扰数据阅读 |
| **响应式适配** | 桌面端表格、移动端卡片，确保各设备可用 |

### 1.3 视觉层级

```
第一层（最高优先级）：正在直播的节目 → 薄荷绿高亮
第二层：价格与优惠信息 → 橙色强调
第三层：节目基础信息 → 白色主文字
第四层：辅助信息（编号、已售） → 灰色次文字
```

---

## 二、配色系统

### 2.1 CSS 变量定义

所有颜色通过 CSS 自定义属性（变量）统一管理，便于全局调整和主题切换。

```css
:root {
  /* === 背景色 === */
  --bg-primary: #0a0a0f;          /* 主背景（近黑色） */
  --bg-card: #12121a;             /* 卡片背景（深灰蓝） */
  --bg-card-hover: #1a1a28;       /* 卡片悬停态 */
  --bg-input: #0e0e16;            /* 输入框背景 */

  /* === 品牌色 === */
  --brand: #ff6b35;               /* 品牌主色（活力橙） */
  --brand-glow: rgba(255, 107, 53, 0.25);  /* 品牌色辉光 */
  --brand-dim: #cc5529;           /* 品牌暗色（按下态） */

  /* === 状态色 === */
  --live: #00d4aa;                /* 正在直播（薄荷绿） */
  --live-glow: rgba(0, 212, 170, 0.3);     /* 直播辉光 */
  --upcoming: #fbbf24;            /* 即将开播（琥珀黄） */
  --ended: #6b7280;               /* 已结束（灰色） */
  --other: #9ca3af;               /* 其他状态 */

  /* === 文字色 === */
  --text-primary: #e8e8ed;        /* 主文字（近白色） */
  --text-secondary: #8888a0;      /* 次文字 */
  --text-muted: #55556a;          /* 弱文字（占位符、禁用态） */

  /* === 边框 === */
  --border: #1e1e2e;              /* 默认边框 */
  --border-light: #2a2a3e;        /* 亮边框（悬停态） */

  /* === 圆角 === */
  --radius: 10px;                 /* 默认圆角 */
  --radius-sm: 6px;               /* 小元素 */
  --radius-lg: 16px;              /* 大容器 */

  /* === 阴影 === */
  --shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
  --shadow-brand: 0 4px 20px rgba(255, 107, 53, 0.25);
}
```

### 2.2 配色使用规则

| 场景 | 使用颜色 | 说明 |
|------|----------|------|
| 页面背景 | `--bg-primary` | body 背景色 |
| 卡片/面板 | `--bg-card` | 所有卡片容器 |
| 按钮-主要 | `--brand` | "开始抓取"按钮 |
| 按钮-悬停 | `--brand` + `--shadow-brand` | hover 时增加辉光阴影 |
| 按钮-次要 | `transparent` + `--border-light` | "下载 Excel"按钮，描边样式 |
| 直播状态 | `--live` | 状态标签、数字高亮 |
| 即将开播 | `--upcoming` | 状态标签 |
| 已结束 | `--ended` | 状态标签 |
| 价格-销售价 | `--brand` | 橙色加粗 |
| 价格-市场价 | `--text-secondary` | 灰色 + 删除线 |
| 优惠标签 | `--upcoming` | 黄色小标签 |
| 日期文字 | `--brand` | 橙色加粗 |
| 表头背景 | `#16161f` | 比 --bg-card 略深 |

### 2.3 背景氛围

通过 `body::before` 伪元素创建微妙的背景氛围，增加页面层次感：

```css
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 200%;
  height: 200%;
  background:
    radial-gradient(ellipse at 15% 15%, rgba(255, 107, 53, 0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 85% 85%, rgba(0, 212, 170, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}
```

- 左上角：橙色径向渐变，4% 透明度
- 右下角：薄荷绿径向渐变，3% 透明度
- 覆盖 200% 面积，确保渐变边缘不出现硬切
- `pointer-events: none` 确保不影响交互

---

## 三、字体规范

### 3.1 字体加载

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap" rel="stylesheet">
```

### 3.2 字体应用

```css
body {
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 400;
  color: var(--text-primary);
  line-height: 1.6;
}
```

### 3.3 字重使用规则

| 字重 | 使用场景 |
|------|----------|
| **300 (Light)** | 辅助说明文字、Footer |
| **400 (Regular)** | 正文、表格内容、按钮文字 |
| **500 (Medium)** | 表头、卡片标题、副标题 |
| **700 (Bold)** | 品牌标题、统计数字、日期、销售价 |
| **900 (Black)** | 品牌标题首字或强调（可选） |

### 3.4 数字排版

所有涉及数字和价格的元素启用等宽数字特性，确保列对齐：

```css
.tabular-nums {
  font-variant-numeric: tabular-nums;
}
```

适用范围：统计数字、价格、已售数量、进度数字。

---

## 四、组件规范

### 4.1 Header 区域

**结构**：品牌标题 + 英文副标题

**样式规范**：

```css
.header {
  text-align: center;
  padding: 40px 20px 24px;
  animation: fadeInDown 0.6s ease-out;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 900;
  background: linear-gradient(135deg, #ff6b35, #ff9a6c, #00d4aa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  line-height: 1.2;
}

.header .subtitle {
  font-size: 0.85rem;
  font-weight: 300;
  color: var(--text-muted);
  letter-spacing: 4px;
  text-transform: uppercase;
}
```

**要点**：
- 标题使用三色渐变（橙 → 浅橙 → 薄荷绿），通过 `background-clip: text` 实现
- 副标题使用弱文字色 + 大字间距，营造高端感
- 入场动画 `fadeInDown 0.6s`

---

### 4.2 控制面板（.control-panel）

**结构**：深色卡片容器，内含三行控件

**容器样式**：

```css
.control-panel {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin: 0 auto 24px;
  max-width: 800px;
  border: 1px solid var(--border);
  animation: fadeInUp 0.6s ease-out 0.1s both;
}
```

**行布局**：每行使用 flex 布局，`gap: 12px`，行间距 `16px`。

#### 4.2.1 按钮组（区域选择 / 天数选择）

```css
.btn-group {
  display: flex;
  gap: 8px;
}

.btn-group .btn {
  padding: 8px 20px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-group .btn:hover {
  border-color: var(--border-light);
  color: var(--text-primary);
  background: var(--bg-card-hover);
}

.btn-group .btn.active {
  border-color: var(--brand);
  color: var(--brand);
  background: rgba(255, 107, 53, 0.1);
}
```

**要点**：
- 默认态：透明背景 + 深色边框 + 次文字色
- 悬停态：亮边框 + 主文字色 + 微弱背景
- 选中态（.active）：品牌色边框 + 品牌色文字 + 品牌色 10% 透明度背景

#### 4.2.2 主按钮（开始抓取）

```css
.btn-primary {
  padding: 10px 28px;
  border-radius: var(--radius);
  border: none;
  background: var(--brand);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-brand);
}

.btn-primary:hover {
  background: #ff7d4d;
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(255, 107, 53, 0.35);
}

.btn-primary:active {
  background: var(--brand-dim);
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
```

#### 4.2.3 次要按钮（下载 Excel）

```css
.btn-secondary {
  padding: 10px 28px;
  border-radius: var(--radius);
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: rgba(255, 107, 53, 0.05);
}
```

#### 4.2.4 第三行布局

```css
.control-panel .action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

- 左侧："开始抓取"主按钮
- 右侧："下载 Excel"次要按钮

---

### 4.3 统计卡片（.stats-grid）

**结构**：3 列 grid 布局，每个卡片包含图标/标签 + 数字 + 描述

**容器样式**：

```css
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  animation: fadeInUp 0.6s ease-out 0.2s both;
}
```

**单个卡片样式**：

```css
.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  border: 1px solid var(--border);
  text-align: center;
  transition: border-color 0.2s ease;
}

.stat-card:hover {
  border-color: var(--border-light);
}

.stat-card .stat-value {
  font-size: 2rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-card .stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 400;
}
```

**三个卡片的数字颜色**：

| 卡片 | 数字颜色 | CSS 类 |
|------|----------|--------|
| 抓取天数 | `var(--brand)` (#ff6b35) | `.stat-value.orange` |
| 节目总数 | `var(--text-primary)` (#e8e8ed) | `.stat-value.white` |
| 正在直播 | `var(--live)` (#00d4aa) | `.stat-value.green` |

---

### 4.4 进度条（.progress-container）

**结构**：外层容器 + 进度条轨道 + 进度条填充 + 文字说明

**显示逻辑**：抓取时显示（`display: block`），抓取完成后隐藏（`display: none`）。

```css
.progress-container {
  display: none;  /* 抓取时改为 block */
  margin-bottom: 24px;
  animation: fadeInUp 0.4s ease-out;
}

.progress-container.visible {
  display: block;
}

.progress-track {
  width: 100%;
  height: 6px;
  background: var(--bg-card);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-bar {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--brand), var(--live));
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: center;
}
```

**要点**：
- 进度条使用橙色到薄荷绿的渐变
- 文字格式："正在抓取 YYYYMMDD（n/total）"
- 进度条宽度通过 JS 动态设置百分比

---

### 4.5 数据表格（桌面端 >= 768px）

#### 4.5.1 表格容器

```css
.table-container {
  overflow-x: auto;
  max-height: 70vh;
  overflow-y: auto;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--bg-card);
}

/* 自定义滚动条 */
.table-container::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.table-container::-webkit-scrollbar-track {
  background: var(--bg-card);
}

.table-container::-webkit-scrollbar-thumb {
  background: var(--border-light);
  border-radius: 3px;
}
```

#### 4.5.2 表格结构

10 列定义：

| 序号 | 列名 | 宽度建议 | 对齐 | 说明 |
|------|------|----------|------|------|
| 1 | 日期 | 100px | left | YYYY-MM-DD 格式，橙色加粗 |
| 2 | 时间 | 70px | center | HH:MM 格式 |
| 3 | 状态 | 90px | center | 药丸形标签 |
| 4 | 商品图片 | 70px | center | 56x56px 缩略图 |
| 5 | 商品名称 | auto | left | 最宽列，左对齐 |
| 6 | 销售价 | 80px | right | 橙色加粗 |
| 7 | 市场价 | 80px | right | 灰色删除线 |
| 8 | 优惠 | 60px | center | 黄色标签 |
| 9 | 已售 | 60px | right | 数字 |
| 10 | 编号 | 80px | center | 灰色小字 |

#### 4.5.3 表头样式

```css
.table-container thead {
  position: sticky;
  top: 0;
  z-index: 10;
}

.table-container thead th {
  background: #16161f;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
  padding: 12px 10px;
  text-align: left;
  white-space: nowrap;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
}
```

**要点**：
- 表头 sticky 固定在顶部
- 背景色 `#16161f`，比卡片背景略深
- 字号 0.8rem，字重 500

#### 4.5.4 表格行样式

```css
.table-container tbody tr {
  border-bottom: 1px solid var(--border);
  transition: background-color 0.15s ease;
}

.table-container tbody tr:hover {
  background-color: var(--bg-card-hover);
}

.table-container tbody td {
  padding: 10px;
  font-size: 0.85rem;
  color: var(--text-primary);
  vertical-align: middle;
}
```

#### 4.5.5 日期分隔线

同一日期的首行顶部显示 2px 橙色分隔线：

```css
.table-container tbody tr.date-first {
  border-top: 2px solid var(--brand);
}
```

**实现逻辑**（JS）：
- 每行都显示日期（不合并单元格）
- 比较当前行日期与上一行日期，如果不同则为当前行添加 `.date-first` 类

#### 4.5.6 日期列样式

```css
td.date-cell {
  color: var(--brand);
  font-weight: 700;
  font-size: 0.85rem;
  white-space: nowrap;
}
```

#### 4.5.7 状态标签

```css
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 999px;  /* 药丸形 */
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

/* 正在直播 */
.status-badge.live {
  background: rgba(0, 212, 170, 0.12);
  color: var(--live);
  border: 1px solid rgba(0, 212, 170, 0.3);
}

.status-badge.live::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--live);
  animation: pulse 1.5s ease-in-out infinite;
}

/* 即将开播 */
.status-badge.upcoming {
  background: rgba(251, 191, 36, 0.12);
  color: var(--upcoming);
  border: 1px solid rgba(251, 191, 36, 0.3);
}

/* 已结束 */
.status-badge.ended {
  background: rgba(107, 114, 128, 0.12);
  color: var(--ended);
  border: 1px solid rgba(107, 114, 128, 0.2);
}
```

#### 4.5.8 商品图片

```css
.product-img {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.product-img:hover {
  transform: scale(2.2);
  z-index: 100;
  position: relative;
  box-shadow: var(--shadow);
}
```

**要点**：
- 默认 56x56px，圆角 8px
- hover 时放大至 2.2 倍，使用 `transform: scale(2.2)` 实现
- 放大时提升 z-index，添加阴影，确保不被其他元素遮挡
- 图片加载失败时显示占位符（灰色背景 + 图标）

#### 4.5.9 价格样式

```css
.price-sale {
  color: var(--brand);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.price-market {
  color: var(--text-secondary);
  text-decoration: line-through;
  font-variant-numeric: tabular-nums;
}
```

#### 4.5.10 优惠标签

```css
.discount-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  background: rgba(251, 191, 36, 0.15);
  color: var(--upcoming);
  font-size: 0.75rem;
  font-weight: 500;
}
```

#### 4.5.11 行入场动画

```css
.table-container tbody tr {
  animation: fadeInUp 0.4s ease-out both;
}

/* 通过 JS 内联 style 设置 animation-delay */
/* delay = min(index * 30ms, 800ms) */
```

**实现逻辑**（JS）：
- 遍历所有 `<tr>`，计算 `animationDelay = Math.min(rowIndex * 30, 800) + 'ms'`
- 通过 `element.style.animationDelay` 设置
- 最大延迟 800ms，避免大量数据时等待过久

---

### 4.6 移动端卡片布局（< 768px）

**切换逻辑**：通过 CSS 媒体查询隐藏表格、显示卡片容器。

```css
@media (max-width: 767px) {
  .table-container {
    display: none;
  }

  .mobile-cards {
    display: block;
  }
}

@media (min-width: 768px) {
  .mobile-cards {
    display: none;
  }
}
```

#### 4.6.1 日期分组标题

```css
.date-group-title {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #16161f;
  color: var(--brand);
  font-weight: 700;
  font-size: 0.9rem;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
}
```

#### 4.6.2 节目卡片

```css
.program-card {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  transition: background-color 0.15s ease;
}

.program-card:hover {
  background-color: var(--bg-card-hover);
}

.program-card .card-image {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.program-card .card-info {
  flex: 1;
  min-width: 0;
}

.program-card .card-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
  /* 单行省略 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.program-card .card-time {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.program-card .card-price {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.program-card .card-price .sale {
  color: var(--brand);
  font-weight: 700;
  font-size: 1rem;
}

.program-card .card-price .market {
  color: var(--text-secondary);
  text-decoration: line-through;
  font-size: 0.8rem;
}
```

**入场动画**：stagger 20ms，与表格类似。

---

### 4.7 Toast 通知

**位置**：右上角固定定位。

```css
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast {
  padding: 12px 20px;
  border-radius: var(--radius);
  font-size: 0.85rem;
  font-weight: 500;
  color: #fff;
  animation: slideInRight 0.3s ease-out;
  box-shadow: var(--shadow);
  max-width: 320px;
}

.toast.success {
  background: var(--live);
}

.toast.error {
  background: #ef4444;
}

.toast.info {
  background: var(--brand);
}

.toast.fade-out {
  animation: slideOutRight 0.3s ease-in forwards;
}
```

**行为规范**：
- 显示时从右侧滑入（`slideInRight`）
- 3 秒后自动消失，滑出动画（`slideOutRight`）
- 同类型 Toast 不重复叠加
- 最多同时显示 3 条

---

### 4.8 Footer

```css
.footer {
  text-align: center;
  padding: 32px 20px;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 300;
  letter-spacing: 1px;
}
```

**内容**：`HAPPIGO PROGRAM SCHEDULE · 数据来源 hao24.com`

---

## 五、动效规范

### 5.1 动画定义

```css
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.4);
    opacity: 0.7;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideOutRight {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(40px);
  }
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
```

### 5.2 动画使用场景

| 动画 | 使用场景 | 参数 |
|------|----------|------|
| `fadeInDown` | Header 入场 | `0.6s ease-out` |
| `fadeInUp` | 控制面板入场 | `0.6s ease-out 0.1s both` |
| `fadeInUp` | 统计卡片入场 | `0.6s ease-out 0.2s both` |
| `fadeInUp` | 表格行入场 | `0.4s ease-out both`，delay = stagger |
| `fadeInUp` | 进度条显示 | `0.4s ease-out` |
| `pulse` | 直播状态圆点 | `1.5s ease-in-out infinite` |
| `spin` | 加载旋转图标 | `1s linear infinite` |
| `slideInRight` | Toast 通知进入 | `0.3s ease-out` |
| `slideOutRight` | Toast 通知退出 | `0.3s ease-in forwards` |
| `shimmer` | 骨架屏加载 | `1.5s ease-in-out infinite` |

### 5.3 骨架屏

加载状态使用 shimmer 效果：

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-card) 25%,
    var(--bg-card-hover) 50%,
    var(--bg-card) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-sm);
}
```

---

## 六、响应式策略

### 6.1 断点定义

| 断点 | 范围 | 布局策略 |
|------|------|----------|
| **桌面端** | >= 1024px | 完整表格，所有列可见 |
| **平板端** | 768px - 1023px | 表格水平滚动，容器 `overflow-x: auto` |
| **移动端** | < 768px | 隐藏表格，切换为卡片布局 |
| **小屏移动端** | < 480px | 统计卡片改为单列，控制面板按钮缩小 |

### 6.2 媒体查询

```css
/* 平板端：表格水平滚动 */
@media (max-width: 1023px) and (min-width: 768px) {
  .table-container {
    overflow-x: auto;
  }

  .table-container table {
    min-width: 900px;  /* 确保表格不会过度压缩 */
  }
}

/* 移动端：卡片布局 */
@media (max-width: 767px) {
  .table-container {
    display: none;
  }

  .mobile-cards {
    display: block;
  }

  .header h1 {
    font-size: 1.8rem;
  }

  .control-panel {
    padding: 16px;
    margin: 0 12px 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin: 0 12px 16px;
  }

  .stat-card {
    padding: 14px 12px;
  }

  .stat-card .stat-value {
    font-size: 1.5rem;
  }
}

/* 小屏移动端 */
@media (max-width: 479px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .control-panel .action-row {
    flex-direction: column;
    gap: 10px;
  }

  .control-panel .action-row .btn-primary,
  .control-panel .action-row .btn-secondary {
    width: 100%;
    text-align: center;
  }

  .btn-group {
    flex-wrap: wrap;
  }

  .btn-group .btn {
    flex: 1;
    min-width: 0;
    text-align: center;
    padding: 8px 12px;
    font-size: 0.8rem;
  }
}
```

### 6.3 响应式字体

```css
.header h1 {
  font-size: clamp(1.6rem, 5vw, 2.5rem);
}
```

---

## 七、状态说明

### 7.1 空状态

页面初始加载或无数据时显示：

```html
<div class="empty-state">
  <div class="empty-icon">📺</div>
  <p class="empty-text">暂无节目数据</p>
  <p class="empty-hint">请选择参数后点击"开始抓取"</p>
</div>
```

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-state .empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state .empty-text {
  font-size: 1rem;
  margin-bottom: 8px;
}

.empty-state .empty-hint {
  font-size: 0.85rem;
  color: var(--text-muted);
  opacity: 0.7;
}
```

### 7.2 加载中状态

**骨架屏**：数据加载时，表格区域显示骨架屏占位。

```html
<!-- 骨架屏行示例 -->
<tr class="skeleton-row">
  <td><div class="skeleton" style="width:80px;height:16px"></div></td>
  <td><div class="skeleton" style="width:50px;height:16px"></div></td>
  <td><div class="skeleton" style="width:60px;height:22px;border-radius:999px"></div></td>
  <td><div class="skeleton" style="width:56px;height:56px;border-radius:8px"></div></td>
  <td><div class="skeleton" style="width:160px;height:16px"></div></td>
  <td><div class="skeleton" style="width:60px;height:16px"></div></td>
  <td><div class="skeleton" style="width:60px;height:16px"></div></td>
  <td><div class="skeleton" style="width:40px;height:16px"></div></td>
  <td><div class="skeleton" style="width:40px;height:16px"></div></td>
  <td><div class="skeleton" style="width:60px;height:16px"></div></td>
</tr>
```

**按钮加载态**：

```css
.btn-primary.loading {
  position: relative;
  color: transparent;
  pointer-events: none;
}

.btn-primary.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 18px;
  height: 18px;
  margin: -9px 0 0 -9px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

### 7.3 错误状态

**网络错误 / 抓取失败**：

- 显示 Toast 通知（error 类型，红色）
- 进度条停止并变为红色
- "开始抓取"按钮恢复可用状态

```css
.progress-bar.error {
  background: #ef4444;
}
```

**图片加载失败**：

```css
.product-img.error,
.card-image.error {
  background: var(--bg-card-hover);
  display: flex;
  align-items: center;
  justify-content: center;
}
```

通过 `onerror` 事件替换为占位图或隐藏。

### 7.4 抓取进行中

- 进度条显示并动态更新
- "开始抓取"按钮变为 loading 态（禁用 + 旋转图标）
- 统计卡片数字实时更新
- 表格数据逐批追加（每次抓取完一天的数据后追加）

### 7.5 抓取完成

- 进度条隐藏
- 按钮恢复正常
- Toast 通知（success 类型）：显示"抓取完成！共获取 X 条节目数据"
- 表格行触发入场动画

---

## 八、全局样式

### 8.1 Reset 与基础

```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 背景氛围层 */
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 200%;
  height: 200%;
  background:
    radial-gradient(ellipse at 15% 15%, rgba(255, 107, 53, 0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 85% 85%, rgba(0, 212, 170, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}
```

### 8.2 内容层级

```css
.app-container {
  position: relative;
  z-index: 1;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}
```

### 8.3 选中与焦点

```css
::selection {
  background: rgba(255, 107, 53, 0.3);
  color: var(--text-primary);
}

:focus-visible {
  outline: 2px solid var(--brand);
  outline-offset: 2px;
}
```

---

## 九、图片占位与错误处理

### 9.1 图片加载占位

```css
.img-placeholder {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  background: var(--bg-card-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 1.2rem;
}
```

### 9.2 图片懒加载

```html
<img class="product-img" data-src="..." alt="商品图片" loading="lazy">
```

通过 `loading="lazy"` 属性实现原生懒加载，或通过 Intersection Observer 实现更精细的控制。

---

## 十、性能注意事项

1. **行入场动画**：stagger delay 最大 800ms，避免大量 DOM 元素同时触发动画导致卡顿
2. **图片**：使用 `loading="lazy"` 延迟加载，商品图片建议使用缩略图 URL
3. **表格滚动**：使用 `max-height: 70vh` + `overflow-y: auto`，避免渲染过多 DOM
4. **动画**：优先使用 `transform` 和 `opacity`，避免触发重排（reflow）
5. **字体**：使用 `font-display: swap` 避免字体加载阻塞渲染
6. **will-change**：对频繁动画的元素（如直播脉冲圆点）可添加 `will-change: transform`

---

## 附录：完整 CSS 变量速查表

```css
:root {
  /* 背景 */
  --bg-primary: #0a0a0f;
  --bg-card: #12121a;
  --bg-card-hover: #1a1a28;
  --bg-input: #0e0e16;

  /* 品牌色 */
  --brand: #ff6b35;
  --brand-glow: rgba(255, 107, 53, 0.25);
  --brand-dim: #cc5529;

  /* 状态色 */
  --live: #00d4aa;
  --live-glow: rgba(0, 212, 170, 0.3);
  --upcoming: #fbbf24;
  --ended: #6b7280;
  --other: #9ca3af;

  /* 文字色 */
  --text-primary: #e8e8ed;
  --text-secondary: #8888a0;
  --text-muted: #55556a;

  /* 边框 */
  --border: #1e1e2e;
  --border-light: #2a2a3e;

  /* 圆角 */
  --radius: 10px;
  --radius-sm: 6px;
  --radius-lg: 16px;

  /* 阴影 */
  --shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
  --shadow-brand: 0 4px 20px rgba(255, 107, 53, 0.25);
}
```
