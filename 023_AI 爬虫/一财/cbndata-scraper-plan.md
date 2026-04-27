# CBNData 免费报告爬虫 + HTML 展示系统 实施计划

## 一、任务理解

### 目标
针对 `https://www.cbndata.com/report` 网站，构建一个完整的爬虫+前端展示系统：
1. **Python Flask 代理服务器**：爬取当年所有免费报告的标题、链接、日期、封面
2. **HTML 前端应用**：展示数据表格（按日期升序、含封面图片），提供下载按钮
3. **PDF 下载功能**：进入报告详情页，按顺序提取图片并保存为 PDF 文件，文件名为报告标题

### 约束
- 图片 URL 带有过期 token（约1小时有效），PDF 下载时需实时获取
- 需要处理 CORS 跨域问题
- 报告图片为带水印的 JPG 格式
- 免费报告当前约 105 页，1256 份（全量），需过滤当年数据

### 预期输出
- 一个可直接运行的 Python 项目（Flask 服务器 + HTML 前端）
- 打开 HTML 即自动抓取当年报告数据并展示
- 每行提供下载按钮，点击生成 PDF 并下载

---

## 二、网站研究结论

### 2.1 数据加载方式
- **混合模式**：SSR（第1页）+ AJAX 无限滚动（后续页）
- 列表页 HTML 中包含 `__INITIAL_STATE__` JS 变量存储初始数据

### 2.2 核心 API 端点

**报告列表 API**：
```
GET https://www.cbndata.com/api/v2/report_products?tags[]=all&price_category=price_free&page=1&per=12
```
- 返回 JSON：`{ data: [...], meta: { current_page, total_page, total_count, per } }`
- 每条报告包含：`id`, `title`, `thumbnail_url`, `date`, `report.images_count`, `tags[]`
- 数据按日期倒序排列（最新在前）

**报告详情页**：
```
GET https://www.cbndata.com/report/{product_id}/detail
```
- HTML 中嵌入 `__INITIAL_STATE__`，包含 `report.watermark_image_urls[]` 数组
- 图片 URL 格式：`https://cfpdf.dtcj.com/{report_id}-{timestamp}-{page:02d}_watermarked.jpg?e={expire}&token={auth}`
- token 有效期约 1 小时

### 2.3 数据结构

**列表项关键字段**：
| 字段 | 说明 | 示例 |
|------|------|------|
| `id` | 产品 ID（用于详情页 URL） | 3354 |
| `title` | 报告标题 | "美妆品牌的..." |
| `thumbnail_url` | 封面图 URL | `https://cf.dtcj.com/{uuid}.png` |
| `date` | 发布日期（ISO 8601） | `2026-04-23T11:00:00.965+08:00` |
| `report.images_count` | 报告总页数 | 19 |
| `tags[].name` | 标签名称 | "美妆个护" |

**详情页关键字段**：
| 字段 | 说明 |
|------|------|
| `report.id` | 报告 ID（用于图片 URL，与产品 ID 不同） |
| `report.watermark_image_urls[]` | 带水印的图片 URL 数组（按页码顺序） |
| `report.images_count` | 总页数 |

---

## 三、系统架构

```
+------------------+       +-------------------+       +------------------+
|   HTML/CSS/JS    | <---> |  Flask 代理服务器  | <---> |  CBNData API/网站 |
|   前端界面        |       |  (Python)          |       |  cbndata.com     |
+------------------+       +-------------------+       +------------------+
                                   |
                                   v
                           +-------------------+
                           |  PDF 生成管线      |
                           |  (img2pdf/Pillow)  |
                           +-------------------+
```

**核心设计**：Flask 服务器作为中间代理，前端只与 Flask 通信，避免跨域问题。图片 token 在每次 PDF 下载时实时获取。

---

## 四、项目结构

```
/workspace/cbndata-scraper/
├── app.py                  # Flask 主应用（路由定义）
├── scraper.py              # CBNData 网站抓取逻辑
├── pdf_generator.py        # 图片下载 + PDF 生成
├── requirements.txt        # Python 依赖
├── templates/
│   └── index.html          # 前端 HTML 页面
└── static/
    ├── css/
    │   └── style.css       # 前端样式
    └── js/
        └── app.js          # 前端交互逻辑
```

---

## 五、实施步骤

### 步骤 1：项目初始化
- 创建目录结构
- 编写 `requirements.txt`（flask, requests, beautifulsoup4, img2pdf, Pillow）
- 安装依赖

### 步骤 2：实现 `scraper.py` — 抓取逻辑模块
- **`get_free_reports()`**：分页遍历 API，过滤当年数据，提前终止优化
  - 请求头必须携带 `Referer: https://www.cbndata.com/report`
  - 遍历分页直到日期早于当前年份
  - 返回精简字段：id, title, date, thumbnail_url, images_count, tags, detail_url
- **`get_report_images(product_id)`**：请求详情页，提取 `__INITIAL_STATE__` 中的 `watermark_image_urls`
  - 使用正则提取 `window.__INITIAL_STATE__ = {...};`
  - 预处理非标准 JSON（`undefined` → `null`，移除尾部逗号）
  - 备选：使用 `json5` 库解析

### 步骤 3：实现 `pdf_generator.py` — PDF 生成模块
- **`download_image(url, save_path)`**：单图下载，支持 3 次重试+指数退避
- **`generate_pdf(image_urls, title)`**：
  1. 创建临时目录
  2. 顺序下载所有图片（stream 模式，避免内存溢出）
  3. 使用 `img2pdf` 无损转换（JPEG 直接嵌入 PDF，不重编码）
  4. 清理临时目录
  5. 返回 `(pdf_bytes, filename)`
- 文件名清理：移除 `\/:*?"<>|` 等非法字符

### 步骤 4：实现 `app.py` — Flask 主应用
- **`GET /`**：返回前端页面
- **`GET /api/reports`**：返回当年免费报告列表（含 5 分钟内存缓存）
- **`GET /api/report/<id>/detail`**：实时获取报告图片 URL（不做缓存）
- **`GET /api/report/<id>/download`**：生成 PDF 并返回文件流
  - 每次调用重新抓取详情页获取新 token
  - 使用 `send_file` 返回 PDF，处理中文文件名（RFC 5987 编码）
  - 使用信号量限制并发 PDF 生成（最多 3 个）

### 步骤 5：实现前端
- **`index.html`**：页面骨架（header + 统计栏 + 加载状态 + 表格 + 下载模态框 + footer）
- **`style.css`**：深色主题 + 琥珀色强调色（呼应 CBNData 品牌色调）
  - 表格行悬停：左侧橙色竖线 + 背景微亮
  - 封面图片：80px 宽，圆角 6px，`object-fit: cover`
  - 下载按钮：橙色渐变，悬停上浮
  - 进度条：橙色渐变 + 微光扫过动画
  - 响应式：桌面表格 / 移动端卡片布局
- **`app.js`**：
  - `fetchReports()`：页面加载时自动调用 `/api/reports`
  - `renderReports()`：按日期升序排列，动态生成表格行
  - `downloadReport(id, title)`：先获取图片 URL，再请求 PDF 下载
  - UI 状态管理：加载中 / 错误 / 进度模态框

### 步骤 6：集成测试与调优
- 端到端测试：打开页面 → 查看列表 → 点击下载 → 验证 PDF
- 边界测试：图片提取失败、部分图片下载失败、大报告（100+页）、中文文件名
- 性能调优：缓存策略、超时配置

---

## 六、关键难点与应对

| 难点 | 应对策略 |
|------|----------|
| 图片 token 过期（~1小时） | 每次下载 PDF 时实时抓取详情页获取新 token；捕获 403 错误自动重试 |
| `__INITIAL_STATE__` 非标准 JSON | 预处理 `undefined→null`、移除尾部逗号；备选 `json5` 库 |
| 大报告 PDF 生成耗时 | 前端显示进度模态框；后端信号量限流；设置合理超时 |
| 封面图片跨域加载失败 | `loading="lazy"` + `onerror` 回退 SVG 占位图 |
| `watermark_image_urls` 字段可能不存在 | 备选方案：从页面 DOM 的 `<img>` 标签中提取图片 URL |

---

## 七、假设与决策

1. **PDF 库选择**：`img2pdf`（无损、快速、JPEG 直接嵌入），而非 `ReportLab`（需重编码）
2. **前端框架**：纯 HTML/CSS/JS（无框架），保持单文件简洁性
3. **数据缓存**：报告列表缓存 5 分钟，图片 URL 不缓存
4. **并发控制**：信号量限制最多 3 个同时 PDF 生成
5. **过滤范围**：仅抓取当前年度（2026年）的免费报告
6. **设计风格**：深色主题 + 琥珀色强调，避免千篇一律的蓝紫色 AI 风格

---

## 八、验证步骤

1. 启动 Flask 服务器：`python app.py`
2. 浏览器打开 `http://localhost:5000`
3. 验证页面自动加载当年报告数据
4. 验证表格按日期升序排列，封面图片正常显示
5. 点击任意报告的"下载 PDF"按钮
6. 验证进度模态框显示正常
7. 验证 PDF 文件下载成功，文件名为报告标题
8. 打开 PDF 验证内容完整（所有页面按顺序排列）
