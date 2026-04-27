# 快乐购节目表 HTML 应用 — 实施计划

## 任务理解

将 Python 爬虫逻辑移植为纯前端 HTML 应用，打开即自动抓取快乐购 TV5 节目表数据，按日期升序展示带商品图片的表格，并提供 Excel 下载功能。

## 关键技术决策

### 1. 跨域方案
目标 API `happigo.com` 未设置 CORS 头，浏览器直接 fetch 会被拦截。采用 **CORS 代理** 方案：
- 使用 `https://api.allorigins.win/raw?url=` 作为代理前缀
- 请求时需手动拼接完整 URL（含 query string）
- 设置 `Referer` 请求头通过 API 校验（allorigins 代理会透传）

### 2. Excel 导出方案
使用 **SheetJS (xlsx)** 库：
- CDN: `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js`
- 支持从 JSON 数据直接生成 .xlsx 文件
- 支持设置列宽、样式等

### 3. 设计风格
采用 **电视购物/直播风格** 的暖色调设计：
- 主色：深色背景 + 金色/橙色点缀（呼应"快乐购"品牌调性）
- 字体：Noto Sans SC（中文）+ 一个有特色的英文字体
- 卡片式布局，按日期分组，每组有日期标题头
- 表格行包含商品缩略图（水平排列）
- 加载动画、状态标签（直播中/即将播出/已结束）带颜色区分

## 实施步骤

### 步骤1：创建 `happigo_schedule.html`

**文件路径**: `/workspace/happigo_schedule.html`

#### 1.1 HTML 结构
```
- header: 标题 "快乐购 TV5 节目表" + 刷新按钮 + 下载Excel按钮
- loading: 加载动画（数据获取时显示）
- summary: 数据概览（日期范围、总节目数）
- main: 按日期分组的节目表格区域
  - 每个日期组：日期标题 + 表格
  - 表格列：序号、商品图片、播出时间、商品名称、商品描述、销售价、市场价、分类、直播状态
- footer: 版权信息
```

#### 1.2 CSS 样式
- CSS 变量定义主题色
- 深色背景 + 卡片式容器
- 表格样式：斑马纹、hover 高亮、圆角
- 直播状态标签颜色：绿色(正在直播)、蓝色(即将播出)、灰色(已结束)
- 商品图片：60x60px 圆角缩略图
- 响应式布局适配不同屏幕
- 加载动画（旋转 + 渐变）

#### 1.3 JavaScript 逻辑

**数据获取** (`fetchSchedule`):
```
1. 计算日期范围：今天往前推6天 ~ 今天（共7天）
2. 对每个日期，通过 CORS 代理请求 API
3. URL 格式: https://api.allorigins.win/raw?url={encodeURIComponent(apiUrl + params)}
4. 解析 JSON 响应，过滤跨天节目（同 Python 逻辑：tvStartTime 转北京时间判断日期）
5. 请求间隔 500ms，避免过快
6. 收集全部数据，按日期升序排列
```

**跨天过滤** (`filterByDate`):
```
- tvStartTime 时间戳 + 8小时偏移 = 北京时间
- 提取日期部分，与查询日期比较
- 不匹配则剔除
```

**渲染表格** (`renderTable`):
```
1. 按日期分组
2. 每组生成日期标题 + <table>
3. 表格行包含 <img> 商品缩略图
4. 直播状态用彩色标签显示
5. 价格格式化（¥前缀）
```

**Excel 导出** (`exportExcel`):
```
1. 使用 SheetJS XLSX.utils.json_to_sheet()
2. 设置列宽
3. 生成 .xlsx 文件并触发下载
4. 文件名：happigo_schedule_YYYYMMDD_YYYYMMDD.xlsx
```

#### 1.4 CDN 依赖
- SheetJS: `https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js`
- Google Fonts: Noto Sans SC + 特色英文字体

### 步骤2：验证
- 在浏览器中打开 HTML 文件
- 确认数据自动加载
- 确认表格按日期升序排列、图片正常显示
- 确认 Excel 下载功能正常

## 输出文件

| 文件 | 说明 |
|------|------|
| `/workspace/happigo_schedule.html` | 完整的 HTML 应用（单文件，含 CSS/JS） |

## 注意事项
1. CORS 代理是第三方服务，可能不稳定，提供多个备选代理自动切换
2. 商品图片来自 `ecimg.happigo.com`，需确认该域名允许图片跨域加载（img 标签通常不受 CORS 限制）
3. Excel 导出不含图片（SheetJS 免费版不支持嵌入图片），但包含图片 URL 列
