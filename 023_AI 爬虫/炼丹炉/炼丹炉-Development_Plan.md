# 炼丹炉行业报告爬虫系统 - 开发计划

## 📋 项目概述

基于对目标网站 `https://www.huo1818.com/report/1` 的技术研究，制定以下开发计划。

### 目标网站技术分析
- **技术栈**: Next.js 服务端渲染 (SSR)
- **数据位置**: JSON 数据嵌入在 HTML 的 `<script id="__NEXT_DATA__">` 标签中
- **数据结构**: `window.__NEXT_DATA__.props.pageProps.reports`
- **分页方式**: URL 参数 `/report/{page}?offset={offset}`
- **反爬措施**: 无明显反爬机制

### 核心数据字段
```json
{
  "reportId": "HYBG20260305000",
  "title": "健康饮料市场消费趋势洞察",
  "coverUrl": "https://static-file-cdn.huo1818.com/banner/xxx.png",
  "pdfUrl": "https://static-file-cdn.huo1818.com/banner/xxx.pdf",
  "publishTime": "2026-03-05 16:52:38",
  "viewCount": 732
}
```

---

## 🏗️ 系统架构

### 三层爬虫架构

```
┌─────────────────────────────────────────────────────────────────┐
│  第一层: API接口探测                                              │
│  - 尝试直接调用后端API                                            │
│  - 分析网络请求寻找JSON端点                                        │
│  - 优先级: 高                                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  第二层: HTML解析 (主方案)                                        │
│  - 使用 requests 获取页面                                         │
│  - BeautifulSoup 提取 script 标签                                 │
│  - 正则/JSON解析提取数据                                          │
│  - 优先级: 高                                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  第三层: Browser Use兜底 (备用)                                   │
│  - Playwright 控制真实浏览器                                      │
│  - 截图+视觉识别获取数据                                          │
│  - 优先级: 中 (网站改版时使用)                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 系统组件图

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (HTML + JS)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   数据展示    │  │   下载管理    │  │   搜索筛选    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python Flask 代理服务器                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   API路由     │  │   爬虫引擎    │  │   文件服务    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     数据层                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  reports.json│  │  downloads/  │  │   缓存文件    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
huo1818_crawler/
├── start.bat                    # Windows一键启动脚本
├── app.py                       # Flask主应用
├── crawler.py                   # 爬虫核心模块
├── requirements.txt             # Python依赖
├── static/
│   ├── css/
│   │   └── style.css           # 样式文件
│   ├── js/
│   │   └── app.js              # 前端逻辑
│   └── downloads/              # PDF下载目录
├── templates/
│   └── index.html              # 主页面
└── data/
    └── reports.json            # 数据存储
```

---

## 📝 开发任务清单

### Phase 1: 基础架构搭建

#### 1.1 创建项目结构
- [ ] 创建项目目录和子文件夹
- [ ] 创建 requirements.txt
- [ ] 创建 .gitignore

#### 1.2 爬虫模块开发 (crawler.py)
```python
# 核心功能
class Hhuo1818Crawler:
    def __init__(self):
        self.base_url = "https://www.huo1818.com/report"
        self.session = requests.Session()
    
    # 第一层: API接口探测
    def try_api_endpoint(self):
        pass
    
    # 第二层: HTML解析 (主方案)
    def parse_html(self, page):
        """
        1. 使用 requests 获取页面
        2. 解析 __NEXT_DATA__ script 标签
        3. 提取 reports 数组
        """
        pass
    
    # 第三层: Browser Use兜底
    def browser_fallback(self, page):
        """
        使用 Playwright 获取页面
        """
        pass
    
    # 全量抓取
    def crawl_all(self):
        """
        遍历所有分页，抓取全量数据
        去重后保存到 JSON
        """
        pass
```

**数据提取规则:**
```python
# HTML中的数据路径
script_tag = soup.find('script', id='__NEXT_DATA__')
data = json.loads(script_tag.string)
reports = data['props']['pageProps']['reports']
```

#### 1.3 Web服务开发 (app.py)
```python
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# API路由
@app.route('/api/reports')
def get_reports():
    """获取所有报告列表"""
    pass

@app.route('/api/reports/refresh', methods=['POST'])
def refresh_reports():
    """手动刷新数据"""
    pass

@app.route('/api/download/<report_id>')
def download_single(report_id):
    """下载单个PDF"""
    pass

@app.route('/api/download/batch', methods=['POST'])
def download_batch():
    """批量下载PDF"""
    pass

@app.route('/api/download/all')
def download_all():
    """下载所有PDF"""
    pass

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')
```

### Phase 2: 前端界面开发

#### 2.1 HTML结构 (templates/index.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>炼丹炉报告爬虫</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="header-left">
            <div class="logo">🔥</div>
            <h1>炼丹炉报告爬虫</h1>
        </div>
        <div class="header-right">
            <button id="refreshBtn">🔄 刷新数据</button>
            <button id="downloadAllBtn">⬇️ 下载全部</button>
        </div>
    </header>
    
    <!-- Toolbar -->
    <div class="toolbar">
        <input type="text" id="searchInput" placeholder="🔍 搜索报告...">
        <select id="sortSelect">
            <option value="time">发布时间</option>
            <option value="views">浏览量</option>
        </select>
        <div class="view-toggle">
            <button data-view="card">卡片</button>
            <button data-view="list">列表</button>
        </div>
    </div>
    
    <!-- Content -->
    <div id="content">
        <!-- 动态加载报告数据 -->
    </div>
    
    <!-- Pagination -->
    <div class="pagination">
        <!-- 分页控件 -->
    </div>
    
    <script src="/static/js/app.js"></script>
</body>
</html>
```

#### 2.2 CSS样式 (static/css/style.css)
- CSS Variables 定义
- Header、Toolbar、Card、List 组件样式
- 响应式媒体查询
- 动画效果

#### 2.3 JavaScript逻辑 (static/js/app.js)
```javascript
// 核心功能
class ReportApp {
    constructor() {
        this.reports = [];
        this.filteredReports = [];
        this.currentPage = 1;
        this.pageSize = 20;
        this.viewMode = 'card';
    }
    
    async init() {
        // 初始化：加载数据
        await this.loadReports();
        this.render();
        this.bindEvents();
    }
    
    async loadReports() {
        // 从API加载报告数据
    }
    
    async refreshData() {
        // 调用刷新API，重新抓取
    }
    
    search(keyword) {
        // 搜索过滤
    }
    
    sort(field) {
        // 排序
    }
    
    render() {
        // 渲染报告列表
    }
    
    downloadSingle(reportId) {
        // 下载单个PDF
    }
    
    downloadBatch(reportIds) {
        // 批量下载
    }
    
    downloadAll() {
        // 下载全部
    }
}
```

### Phase 3: 功能完善

#### 3.1 数据去重与存储
- 使用 `reportId` 作为主键
- JSON文件存储结构
- 增量更新逻辑

#### 3.2 PDF下载功能
- 单条下载：直接跳转PDF链接
- 批量下载：生成ZIP文件
- 文件名处理：清理非法字符

#### 3.3 启动脚本 (start.bat)
```batch
@echo off
echo Starting Huo1818 Report Crawler...
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed!
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

REM Start the server
start http://localhost:5000
python app.py

pause
```

### Phase 4: 测试与优化

#### 4.1 功能测试
- [ ] 爬虫能正确抓取所有分页数据
- [ ] 数据去重功能正常
- [ ] 前端展示正确
- [ ] 搜索、排序功能正常
- [ ] 单条/批量/全量下载功能正常

#### 4.2 异常处理
- [ ] 网络异常重试机制
- [ ] 网站结构变更检测
- [ ] 错误提示和日志

#### 4.3 性能优化
- [ ] 请求频率控制
- [ ] 数据缓存
- [ ] 前端分页优化

---

## 🔧 技术规格

### Python依赖 (requirements.txt)
```
flask>=2.0.0
requests>=2.28.0
beautifulsoup4>=4.11.0
playwright>=1.30.0
```

### API接口规范

| 接口 | 方法 | 参数 | 返回 |
|------|------|------|------|
| /api/reports | GET | - | JSON数组 |
| /api/reports/refresh | POST | - | {updated: N} |
| /api/download/`<id>` | GET | report_id | PDF文件 |
| /api/download/batch | POST | {ids: []} | ZIP文件 |
| /api/download/all | GET | - | ZIP文件 |

### 数据存储格式 (data/reports.json)
```json
{
  "reports": [
    {
      "reportId": "HYBG20260305000",
      "title": "健康饮料市场消费趋势洞察",
      "coverUrl": "https://...",
      "pdfUrl": "https://...",
      "publishTime": "2026-03-05 16:52:38",
      "viewCount": 732,
      "detailUrl": "https://www.huo1818.com/report/1"
    }
  ],
  "lastUpdate": "2026-05-26T10:00:00",
  "totalCount": 64
}
```

---

## 📅 开发时间线

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| Phase 1 | 基础架构搭建 | 2小时 |
| Phase 2 | 前端界面开发 | 3小时 |
| Phase 3 | 功能完善 | 2小时 |
| Phase 4 | 测试与优化 | 1小时 |
| **总计** | | **8小时** |

---

## ✅ 验收标准

1. **爬虫功能**
   - [ ] 能抓取全部8页数据
   - [ ] 数据去重正确
   - [ ] 支持增量更新

2. **Web应用**
   - [ ] 页面美观、响应式
   - [ ] 搜索、排序功能正常
   - [ ] 卡片/列表视图切换正常

3. **下载功能**
   - [ ] 单条下载正常
   - [ ] 批量下载生成ZIP
   - [ ] 全量下载生成ZIP
   - [ ] 文件名正确（使用报告标题）

4. **启动脚本**
   - [ ] 双击start.bat自动启动
   - [ ] 自动打开浏览器
   - [ ] 自动安装依赖

---

## 🚀 后续优化方向

1. **v1.1**
   - 定时自动更新
   - 下载进度显示
   - 数据导出Excel

2. **v1.2**
   - 数据可视化图表
   - 邮件通知
   - 多用户支持

---

## 📞 联系方式

如有问题，请联系开发团队。

---

**计划制定日期**: 2026-05-26  
**版本**: v1.0
