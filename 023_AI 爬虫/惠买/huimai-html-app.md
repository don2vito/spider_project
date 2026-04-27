# 惠买网电视购物节目表 - HTML应用开发计划

## 任务理解

**目标**：基于已有的Python爬虫逻辑和API分析文档，创建一个单文件HTML应用。打开后自动从 `www.huimai.com.cn/tvList` 抓取节目数据，按频道+日期升序展示，并提供Excel下载功能。

**关键约束**：
- 单个HTML文件，无后端依赖
- 前端直接调用 `https://www.huimai.com.cn/getTvList` API（已验证可跨域访问）
- 使用SheetJS CDN实现Excel导出
- 数据按频道（优购物→爱家购物）、日期（升序）排序

---

## 技术方案

### API接口（来自Python代码和MD文档）

| 项目 | 值 |
|------|-----|
| URL | `https://www.huimai.com.cn/getTvList` |
| 方法 | POST |
| Content-Type | `application/x-www-form-urlencoded` |
| 参数 | `channel` (UGO1/BTV1) + `date` (Unix时间戳) |
| Headers | `Referer: https://www.huimai.com.cn/tvList` |

### 数据提取字段

日期、星期、频道、开始时间、结束时间、商品ID、商品名称、售价、原价、活动标签、是否直播、商品链接

### 技术栈

- **HTML/CSS/JS**：单文件，无框架
- **SheetJS CDN**：`https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js` — Excel导出
- **字体**：Google Fonts（选一个有辨识度的中文字体组合）
- **设计风格**：电视购物/直播主题 — 深色背景 + 红色/金色accent，营造直播间的视觉氛围

### 设计方向

- **风格**：深色主题 + 红金accent，模拟电视购物直播间氛围
- **布局**：顶部状态栏（加载进度）→ 频道Tab切换 → 日期分组卡片列表 → 底部下载按钮
- **动效**：加载骨架屏、卡片淡入、直播标记脉冲动画
- **响应式**：适配桌面和移动端

---

## 实施步骤

### Step 1: 创建HTML文件 `/workspace/huimai_tvlist.html`

**页面结构**：
```
<header> — 标题 + 刷新按钮 + 下载Excel按钮
<main>
  <div class="stats-bar"> — 统计信息（总节目数、频道数、日期范围）
  <div class="channel-tabs"> — 频道筛选Tab（全部/优购物/爱家购物）
  <div class="program-list"> — 节目卡片列表，按日期分组
    <div class="date-group"> — 日期标题
      <div class="program-card"> — 单个节目卡片
        时间段 | 商品图片 | 商品名称 | 价格 | 标签 | 直播标记
</main>
<footer> — 数据来源说明
```

### Step 2: JavaScript核心逻辑

1. **数据抓取** (`fetchTVList`)：
   - 遍历2个频道 × 7天 = 14次API调用
   - 使用 `fetch` + POST + URLSearchParams
   - 设置正确的Headers（Referer等）
   - 并发控制（同时最多3个请求）
   - 错误重试机制

2. **日期工具**：
   - `getDateTimestamp(dateStr)` — 日期→Unix时间戳（东八区）
   - `getDateRange(days)` — 最近N天日期列表
   - `getWeekdayName(dateStr)` — 星期名称

3. **数据解析** (`parseTVList`)：
   - 从 `data.tvItemList` 二维数组提取每个商品
   - 映射字段：begin/end/goodsName/price/shopPrice/actLabelDesc/isLiving等

4. **排序** (`sortPrograms`)：
   - 先按频道排序（优购物在前）
   - 再按日期升序
   - 最后按开始时间升序

5. **渲染** (`renderPrograms`)：
   - 按日期分组渲染卡片
   - 频道Tab筛选
   - 搜索/过滤功能

6. **Excel导出** (`exportToExcel`)：
   - 使用SheetJS `XLSX.utils.json_to_sheet` + `XLSX.writeFile`
   - 导出字段：日期、星期、频道、开始时间、结束时间、商品名称、售价、原价、活动标签、是否直播、商品链接

### Step 3: CSS样式

- 深色主题（#0f0f0f 背景）
- 红色accent（#E53935）用于直播标记和CTA按钮
- 金色accent（#FFD700）用于价格高亮
- 卡片式布局，hover效果
- 加载状态骨架屏
- 直播标记脉冲动画
- 响应式适配

---

## 验证步骤

1. 打开HTML文件，确认自动发起API请求并展示数据
2. 验证两个频道（优购物/爱家购物）数据均正确加载
3. 验证数据按频道+日期升序排列
4. 验证频道Tab筛选功能正常
5. 验证Excel下载功能，检查导出文件内容完整
6. 验证加载状态和错误处理
