# 网易数读栏目爬虫系统开发计划

## 一、项目概述

### 1.1 项目目标
开发一个完整的网易新闻数读栏目数据爬取系统，包含：
- Python代理服务器（后端爬虫服务）
- HTML前端应用（数据展示与下载界面）
- 一键启动脚本（.bat文件）

### 1.2 目标网站分析
- **主页面**: `https://data.163.com/special/datablog/`
- **数据结构**: 服务端渲染，数据嵌入在JavaScript变量 `ohnofuchlist` 中
- **文章详情页**: `https://www.163.com/data/article/{文章ID}.html`
- **图片CDN**: `https://nimg.ws.126.net/`

### 1.3 数据字段
- `url`: 文章详情页链接
- `title`: 文章标题
- `img`: 封面图片URL
- `time`: 发布时间
- `comment`: 评论数量
- `keyword`: 关键词标签

---

## 二、技术架构

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     用户浏览器                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              前端 HTML 应用                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │   │
│  │  │  数据展示表格  │  │  下载按钮    │  │ 进度显示 │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP API
┌───────────────────────────▼─────────────────────────────────┐
│                  Python Flask 代理服务器                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              爬虫引擎模块                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │   │
│  │  │ 第一层: API  │  │ 第二层: HTML │  │ 第三层:  │  │   │
│  │  │   接口尝试    │  │   解析提取   │  │ Browser  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              PDF生成模块                             │   │
│  │  - 图片下载                                          │   │
│  │  - PDF合并生成                                       │   │
│  │  - 批量/单份下载                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈
- **后端**: Python 3.8+, Flask, requests, BeautifulSoup4, Pillow, reportlab
- **前端**: HTML5, CSS3, JavaScript (原生)
- **浏览器自动化**: Playwright (第三层兜底方案)

---

## 三、三层爬虫策略

### 3.1 第一层：API接口尝试
**状态**: 经研究，网易数读栏目没有公开的分页JSON API接口

**实现逻辑**:
1. 尝试访问已知的网易新闻API端点
2. 如果返回有效数据，直接解析JSON
3. 如果失败，自动降级到第二层

**代码位置**: `crawler/api_layer.py`

### 3.2 第二层：HTML解析（主方案）
**状态**: ✅ 推荐方案，经测试可行

**实现逻辑**:
1. 发送HTTP GET请求获取列表页HTML
2. 使用正则表达式提取 `ohnofuchlist` JavaScript变量
3. 解析JSON数据获取文章列表
4. 对每个文章详情页，使用BeautifulSoup解析DOM获取所有图片

**关键代码**:
```python
# 提取列表数据
pattern = r'var ohnofuchlist=(\[.*?\]);'
match = re.search(pattern, html, re.DOTALL)
articles = json.loads(match.group(1))

# 提取详情页图片
soup = BeautifulSoup(html, 'html.parser')
content_div = soup.find('div', class_='post_body')
images = [img.get('src') for img in content_div.find_all('img')]
```

**代码位置**: `crawler/html_parser.py`

### 3.3 第三层：Browser Use智能兜底
**状态**: 备用方案，当HTML解析失效时启用

**实现逻辑**:
1. 使用Playwright启动无头浏览器
2. 访问列表页，等待JavaScript渲染完成
3. 截取页面截图，使用大模型视觉能力识别数据
4. 或直接从浏览器环境提取页面变量

**代码位置**: `crawler/browser_layer.py`

---

## 四、模块设计

### 4.1 后端模块结构

```
server/
├── app.py                  # Flask主应用入口
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
├── crawler/
│   ├── __init__.py
│   ├── base.py             # 爬虫基类
│   ├── api_layer.py        # 第一层：API接口
│   ├── html_parser.py      # 第二层：HTML解析
│   ├── browser_layer.py    # 第三层：Browser Use
│   └── pdf_generator.py    # PDF生成器
├── utils/
│   ├── __init__.py
│   ├── cache.py            # 缓存管理
│   └── helpers.py          # 工具函数
└── data/                   # 数据存储目录
    ├── downloads/          # 下载的PDF文件
    └── cache/              # 缓存数据
```

### 4.2 API接口设计

#### 4.2.1 获取文章列表
```
GET /api/articles

Response:
{
    "success": true,
    "data": [
        {
            "id": "KTP4DKNB00019GOE",
            "title": "被朝鲜包围的中国村庄，韩国人曾来这里盗墓",
            "url": "https://www.163.com/data/article/KTP4DKNB00019GOE.html",
            "cover_image": "https://nimg.ws.126.net/...",
            "publish_time": "2026-05-25 10:39:42",
            "comment_count": "5",
            "keywords": "朝鲜,满浦,集安,朝鲜半岛,中朝"
        }
    ],
    "total": 100,
    "timestamp": "2026-05-27T10:00:00"
}
```

#### 4.2.2 获取文章详情
```
GET /api/articles/<article_id>

Response:
{
    "success": true,
    "data": {
        "id": "KTP4DKNB00019GOE",
        "title": "被朝鲜包围的中国村庄，韩国人曾来这里盗墓",
        "url": "https://www.163.com/data/article/KTP4DKNB00019GOE.html",
        "content_images": [
            "https://nimg.ws.126.net/...",
            "https://nimg.ws.126.net/..."
        ],
        "content_text": "..."
    }
}
```

#### 4.2.3 生成PDF
```
POST /api/articles/<article_id>/pdf

Response:
{
    "success": true,
    "data": {
        "pdf_url": "/downloads/被朝鲜包围的中国村庄.pdf",
        "filename": "被朝鲜包围的中国村庄.pdf",
        "page_count": 5
    }
}
```

#### 4.2.4 批量生成PDF
```
POST /api/articles/batch/pdf

Request Body:
{
    "article_ids": ["KTP4DKNB00019GOE", "KTCFRUT6000181IU"]
}

Response:
{
    "success": true,
    "data": {
        "zip_url": "/downloads/batch_20260527_100000.zip",
        "total": 2,
        "success_count": 2,
        "failed_count": 0
    }
}
```

#### 4.2.5 刷新数据
```
POST /api/refresh

Response:
{
    "success": true,
    "data": {
        "new_count": 5,
        "total_count": 105,
        "timestamp": "2026-05-27T10:00:00"
    }
}
```

---

## 五、前端设计

### 5.1 页面结构

```
┌─────────────────────────────────────────────────────────────┐
│  🕷️ 网易数读爬虫系统                    [刷新数据] [设置]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 数据统计                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  总报告数   │  │  今日新增   │  │  已下载    │            │
│  │    105     │  │     5      │  │    12      │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  🔍 搜索: [________________]  筛选: [全部 ▼]                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📷 封面    报告名称                    操作        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  [图片]    被朝鲜包围的中国村庄...      [下载] [预览]│   │
│  │  [图片]    一亿中国人，因为它精神...    [下载] [预览]│   │
│  │  [图片]    中国最容易背锅的专业...      [下载] [预览]│   │
│  │  ...                                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [全选]  [批量下载选中]  [下载全部]                         │
│                                                             │
│                    ← 1 2 3 4 5 →                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 功能特性
- **自动抓取**: 页面加载时自动获取最新数据
- **数据去重**: 使用文章ID进行去重，避免重复爬取
- **本地缓存**: 使用localStorage缓存数据，减少重复请求
- **进度显示**: 下载时显示实时进度条
- **批量操作**: 支持全选、批量下载
- **PDF预览**: 生成PDF前可预览图片列表

### 5.3 文件结构

```
frontend/
├── index.html              # 主页面
├── css/
│   ├── style.css           # 主样式
│   └── components.css      # 组件样式
├── js/
│   ├── app.js              # 主应用逻辑
│   ├── api.js              # API调用封装
│   ├── table.js            # 表格组件
│   └── pdf.js              # PDF下载管理
└── assets/
    ├── logo.png
    └── loading.gif
```

---

## 六、PDF生成方案

### 6.1 技术选型
- **库**: `reportlab` + `Pillow`
- **方案**: 下载详情页所有图片 → 按顺序合并为PDF

### 6.2 实现流程
1. 访问文章详情页URL
2. 解析HTML获取所有内容图片URL
3. 下载图片到临时目录
4. 使用Pillow打开图片，转换为RGB模式
5. 使用reportlab生成PDF，每页一张图片
6. 清理临时文件

### 6.3 代码示例
```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
import requests
import io

def generate_pdf(title, image_urls, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    for img_url in image_urls:
        # 下载图片
        response = requests.get(img_url)
        img = Image.open(io.BytesIO(response.content))
        
        # 计算缩放比例
        img_width, img_height = img.size
        scale = min(width / img_width, height / img_height)
        new_width = img_width * scale
        new_height = img_height * scale
        
        # 居中绘制
        x = (width - new_width) / 2
        y = (height - new_height) / 2
        
        c.drawImage(img, x, y, width=new_width, height=new_height)
        c.showPage()
    
    c.save()
```

---

## 七、一键启动方案

### 7.1 start.bat 内容
```batch
@echo off
chcp 65001 >nul
title NetEase Data Blog Crawler

echo ==========================================
echo   NetEase Data Blog Crawler System
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "server\venv" (
    echo [INFO] Creating virtual environment...
    python -m venv server\venv
)

echo [INFO] Activating virtual environment...
call server\venv\Scripts\activate.bat

echo [INFO] Installing dependencies...
pip install -q -r server\requirements.txt

echo [INFO] Starting server...
start "Crawler Server" python server\app.py

echo [INFO] Waiting for server to start...
timeout /t 3 /nobreak >nul

echo [INFO] Opening browser...
start "" "http://127.0.0.1:5000"

echo.
echo ==========================================
echo   Server running at http://127.0.0.1:5000
echo   Press any key to stop server
echo ==========================================
pause >nul

echo [INFO] Stopping server...
taskkill /F /IM python.exe >nul 2>&1

echo [INFO] Done.
```

---

## 八、开发任务清单

### 8.1 后端开发
- [ ] 创建Flask应用框架
- [ ] 实现HTML解析爬虫（第二层）
- [ ] 实现API接口尝试（第一层）
- [ ] 实现Browser Use兜底（第三层）
- [ ] 实现PDF生成功能
- [ ] 实现数据缓存机制
- [ ] 编写API路由

### 8.2 前端开发
- [ ] 创建HTML页面结构
- [ ] 实现CSS样式
- [ ] 实现数据表格组件
- [ ] 实现搜索筛选功能
- [ ] 实现下载管理功能
- [ ] 实现进度显示

### 8.3 集成测试
- [ ] 测试爬虫各层级
- [ ] 测试PDF生成功能
- [ ] 测试批量下载
- [ ] 测试一键启动脚本

---

## 九、依赖清单

### 9.1 Python依赖 (requirements.txt)
```
flask==2.3.3
flask-cors==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
Pillow==10.0.1
reportlab==4.0.6
playwright==1.40.0
```

---

## 十、注意事项

### 10.1 反爬策略应对
- 使用随机User-Agent
- 添加请求间隔（1-2秒）
- 使用代理池（可选）
- 限制并发请求数

### 10.2 数据去重
- 使用文章ID作为主键
- 本地SQLite数据库存储已爬取记录
- 每次启动时检查重复数据

### 10.3 错误处理
- 网络超时重试（3次）
- 图片下载失败跳过
- 详细日志记录

---

## 十一、文件输出位置

所有开发文件将输出到：
```
/workspace/netease_crawler/
├── server/                 # Python后端代码
├── frontend/               # HTML前端代码
├── start.bat               # 一键启动脚本
├── PRD.md                  # 产品需求文档
└── UI.md                   # UI设计文档
```
