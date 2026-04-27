# 环球购物节目表 HTML应用开发计划

## 摘要

将已有的Python爬虫逻辑（签名算法 + API调用 + 数据解析）移植到一个单文件HTML应用中。用户打开HTML即可自动抓取全部日期的节目数据，按日期升序展示，并提供Excel下载功能。

## 当前状态分析

### 已有资产
- **Python爬虫** (`shark_shopping_spider.py`)：包含完整的签名算法、3个API接口调用、数据解析逻辑
- **API逆向文档** (`shark-shopping-spider-plan.md`)：详细的接口说明和数据结构

### 需要移植到HTML的核心逻辑

1. **签名算法**：双重MD5 — `MD5(MD5(排序拼接参数).upper() + 密钥).upper()`
   - 密钥：`e662633040d6a433d48580a38fcedc49c9ba5d015dccf701096abade0c623163`
   - 参数按key ASCII升序排序，跳过null/array，拼接key+value

2. **3个API接口**：
   - `tv.program.date` → 获取可查询日期列表
   - `tv.program.data` → 获取指定日期节目数据
   - `tv.program.categories` → 获取分类列表（可选）

3. **数据解析**：Unix时间戳→HH:MM、优惠信息提取、字段映射

### 关键技术挑战
- **CORS跨域**：浏览器直接请求 `api.sharkshopping.com` 可能被CORS策略阻止
  - **解决方案**：使用CORS代理（如 `https://api.allorigins.win/raw?url=`）或在前端代码中提供多个备用代理
- **MD5计算**：浏览器端无原生MD5，需内嵌轻量MD5库（SparkMD5 ~5KB）
- **Excel导出**：使用SheetJS (xlsx) CDN库生成.xlsx文件

## 实施方案

### 步骤1：创建单文件HTML应用 `shark_shopping_viewer.html`

**文件位置**：`/workspace/shark_shopping_viewer.html`

#### 设计风格
- **主题**：电视购物/直播风格，深色背景 + 金色/红色点缀
- **布局**：顶部标题栏 → 日期标签导航 → 数据表格 → 底部下载按钮
- **动效**：加载动画、数据渐入、hover高亮

#### HTML结构
```
<header> — 标题 + 频道信息 + 刷新按钮
<nav> — 日期标签（可点击切换/筛选）
<main>
  <section#stats> — 统计概览（总节目数、日期范围、分类分布）
  <section#table> — 数据表格（按日期分组，升序排列）
</main>
<footer> — 下载Excel按钮 + 数据更新时间
```

#### JavaScript模块（全部内嵌）

1. **MD5模块**：内嵌SparkMD5库（压缩版）
2. **签名模块**：`generateSign(params)` — 移植Python的签名算法
3. **API模块**：
   - `fetchAvailableDates()` — 获取日期列表
   - `fetchProgramData(date)` — 获取单日节目数据
   - `fetchAllData()` — 自动获取全部日期数据（串行请求，带延迟）
4. **数据解析模块**：`parseProgramItem(item)` — 移植Python解析逻辑
5. **UI渲染模块**：
   - `renderDateNav(dates)` — 渲染日期标签导航
   - `renderTable(programs)` — 渲染数据表格
   - `renderStats(programs)` — 渲染统计信息
6. **Excel导出模块**：使用SheetJS CDN生成并下载.xlsx文件
7. **CORS代理模块**：封装fetch请求，自动处理CORS代理

#### 表格列定义
| 列名 | 字段 | 说明 |
|------|------|------|
| 日期 | real_date | YYYY-MM-DD |
| 开始时间 | start_time | HH:MM |
| 结束时间 | end_time | HH:MM |
| 分类 | cat_name | 节目分类 |
| 品牌 | brand_name | 商品品牌 |
| 商品名称 | goods.name | 商品名 |
| SKU | goods.sku | 商品编号 |
| 手机价 | goods.price | 销售价格 |
| 市场价 | goods.marketprice | 原价 |
| 优惠信息 | label | 折扣/立减信息 |
| 商品链接 | goods.wapUrl | 购买链接 |

#### 外部CDN依赖
- **SheetJS**：`https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js`（Excel导出）
- **MD5**：内嵌SparkMD5（避免额外CDN依赖）

### 步骤2：测试验证
- 在浏览器中打开HTML文件
- 验证自动抓取全部日期数据
- 验证数据按日期升序排列
- 验证Excel下载功能
- 验证日期标签筛选功能

## 假设与决策
1. **CORS处理**：优先尝试直接请求；若被阻止，自动切换到CORS代理
2. **单文件设计**：所有CSS/JS内嵌，无外部文件依赖（除SheetJS CDN）
3. **Excel格式**：使用.xlsx格式（非.csv），包含表头样式
4. **自动刷新**：每次打开页面自动抓取最新数据，同时提供手动刷新按钮
5. **串行请求**：日期数据逐个请求（避免并发过多），每个请求间隔300ms

## 验证步骤
1. 浏览器打开HTML，确认自动加载动画和数据抓取
2. 对比网页原始数据，验证数据完整性和准确性
3. 点击日期标签，验证筛选功能
4. 点击下载Excel，验证文件内容和格式
5. 测试手动刷新功能
