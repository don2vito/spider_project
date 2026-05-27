# 艾瑞咨询研究报告爬虫系统 - 开发计划文档

## 项目概述

开发一个针对艾瑞咨询研究报告网站 (`https://www.iresearch.com.cn/report.shtml`) 的全量数据爬取系统，包含 Python 代理服务器和 HTML 前端应用，支持一键启动和批量下载 PDF 报告。

---

## 一、网站技术分析

### 1.1 发现的 API 接口

通过浏览器网络监控，已识别以下关键 API：

| API 端点 | 用途 | 方法 |
|---------|------|------|
| `/api/products/GetReportList?fee=0&date=&lastId=&pageSize=12` | 获取报告列表 | GET |
| `/api/Detail/reportM?id={id}&isfree=0` | 获取报告详情 | GET |

### 1.2 分页机制

- **游标分页**：使用 `lastId` 参数进行分页
- 初始请求：`lastId=` (空)
- 下一页：`lastId=freport.{最后一条记录的Id}`
- 每页数量：`pageSize` 参数控制（默认12条）

### 1.3 数据结构

**报告列表项字段：**
```json
{
  "Id": "freport.4822",
  "NewsId": 4822,
  "Title": "报告标题",
  "sTitle": "短标题",
  "Content": "报告摘要",
  "BigImg": "封面图URL",
  "SmallImg": "缩略图URL",
  "VisitUrl": "详情页URL",
  "Uptime": "发布时间",
  "industry": "行业分类",
  "Keyword": ["关键词"],
  "Author": "作者",
  "views": 353,
  "Price": 0
}
```

**报告详情字段：**
```json
{
  "id": 4822,
  "Title": "报告标题",
  "Topic": "封面图URL",
  "Content": "HTML格式内容",
  "GraphList": "图表列表文本",
  "PagesCount": 39,
  "TuijianText": "推荐文本",
  "Uptime": "发布时间",
  "industry": "行业分类",
  "keywords": "关键词",
  "isFree": 0
}
```

### 1.4 PDF 下载机制

- 点击"报告下载"按钮后弹出登录框
- PDF 下载需要登录验证
- 免费报告可直接下载，付费报告需要购买
- PDF 文件命名规则：`{报告标题}.pdf`

---

## 二、系统架构设计

### 2.1 三层爬取策略

```
┌─────────────────────────────────────────────────────────────┐
│                      三层爬取架构                            │
├─────────────────────────────────────────────────────────────┤
│  第一层：API 接口层 (优先级最高)                              │
│  ├── 直接调用 /api/products/GetReportList 获取列表           │
│  └── 直接调用 /api/Detail/reportM 获取详情                   │
├─────────────────────────────────────────────────────────────┤
│  第二层：HTML 解析层 (API 失效时备用)                         │
│  ├── BeautifulSoup 解析服务端渲染的 HTML                     │
│  └── XPath 提取报告信息                                      │
├─────────────────────────────────────────────────────────────┤
│  第三层：Browser Use 层 (前两层都失效时兜底)                  │
│  ├── Playwright 控制真实浏览器                               │
│  └── 截图 + 大模型视觉识别提取数据                            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 系统组件

```
┌─────────────────┐     HTTP API      ┌──────────────────┐
│   HTML 前端     │ ◄────────────────► │  Python 代理服务  │
│  (浏览器运行)    │                   │   (Flask/FastAPI) │
└─────────────────┘                   └────────┬─────────┘
                                               │
                          ┌────────────────────┼────────────────────┐
                          ▼                    ▼                    ▼
                   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
                   │  API 爬取器  │      │ HTML 解析器  │      │ Browser Use │
                   │  (Layer 1)  │      │ (Layer 2)   │      │ (Layer 3)   │
                   └─────────────┘      └─────────────┘      └─────────────┘
```

---

## 三、文件结构

```
iresearch_crawler/
├── server.py              # Python 代理服务器 (Flask/FastAPI)
├── crawler.py             # 三层爬取逻辑实现
├── index.html             # 前端 HTML 应用
├── start.bat              # Windows 一键启动脚本
├── requirements.txt       # Python 依赖
└── downloads/             # 下载的 PDF 文件存储目录
    └── .gitkeep
```

---

## 四、详细实现方案

### 4.1 Python 代理服务器 (server.py)

**功能模块：**
1. **API 路由**
   - `GET /api/crawl` - 触发全量爬取任务
   - `GET /api/reports` - 获取已爬取的报告列表（支持搜索、筛选、分页）
   - `GET /api/industries` - 获取行业分类列表
   - `GET /api/download/{id}` - 下载单个报告 PDF（需登录）
   - `POST /api/download/batch` - 批量下载报告（需登录）
   - `GET /api/status` - 获取爬取状态
   - `POST /api/auth/login` - 手机号登录（发送验证码）
   - `POST /api/auth/verify` - 验证验证码完成登录
   - `POST /api/auth/logout` - 退出登录
   - `GET /api/auth/status` - 获取登录状态

2. **爬取器类 (Crawler)**
   - `crawl_api_layer()` - 第一层：API 接口爬取
   - `crawl_html_layer()` - 第二层：HTML 解析爬取
   - `crawl_browser_layer()` - 第三层：Browser Use 爬取
   - `deduplicate()` - 数据去重
   - `save_to_json()` - 保存数据

3. **下载器类 (Downloader)**
   - `download_pdf()` - 下载单个 PDF
   - `download_batch()` - 批量下载
   - `sanitize_filename()` - 文件名清理

4. **筛选器类 (Filter)**
   - `search_reports()` - 按关键词搜索报告
   - `filter_by_industry()` - 按行业筛选
   - `filter_by_date_range()` - 按时间范围筛选
   - `sort_reports()` - 排序报告列表
   - `combine_filters()` - 组合多个筛选条件

5. **认证类 (Auth)**
   - `send_verification_code()` - 发送验证码（模拟）
   - `verify_code()` - 验证验证码
   - `check_login_status()` - 检查登录状态
   - `generate_token()` - 生成登录令牌
   - `logout()` - 退出登录

**技术选型：**
- Web 框架：Flask (轻量，适合本地代理)
- HTTP 请求：requests + aiohttp (异步)
- HTML 解析：BeautifulSoup4 + lxml
- 浏览器控制：Playwright (第三层兜底)
- CORS 支持：flask-cors
- 认证：JWT Token (本地模拟，无需真实短信服务)

### 4.2 爬取逻辑 (crawler.py)

**第一层 - API 接口爬取：**
```python
async def crawl_api_layer():
    base_url = "https://www.iresearch.com.cn/api/products/GetReportList"
    all_reports = []
    last_id = ""
    
    while True:
        params = {"fee": "0", "date": "", "lastId": last_id, "pageSize": 50}
        response = await fetch(base_url, params)
        reports = response.get("List", [])
        
        if not reports:
            break
            
        all_reports.extend(reports)
        last_id = reports[-1]["Id"]
        
        # 获取详情
        for report in reports:
            detail = await fetch_detail(report["NewsId"])
            report["detail"] = detail
    
    return all_reports
```

**第二层 - HTML 解析爬取：**
```python
def crawl_html_layer():
    url = "https://www.iresearch.com.cn/report.shtml"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # XPath 等效 CSS 选择器
    reports = soup.select('.report-item')  # 根据实际 DOM 调整
    data = []
    for report in reports:
        data.append({
            'title': report.select_one('.title').text,
            'link': report.select_one('a')['href'],
            'image': report.select_one('img')['src']
        })
    return data
```

**第三层 - Browser Use 爬取：**
```python
async def crawl_browser_layer():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.iresearch.com.cn/report.shtml")
        
        # 等待内容加载
        await page.wait_for_selector('.report-list')
        
        # 提取数据
        reports = await page.evaluate('''() => {
            const items = document.querySelectorAll('.report-item');
            return Array.from(items).map(item => ({
                title: item.querySelector('.title').innerText,
                link: item.querySelector('a').href,
                image: item.querySelector('img').src
            }));
        }''')
        
        await browser.close()
        return reports
```

### 4.3 前端 HTML 应用 (index.html)

**页面结构：**
1. **头部区域**
   - 标题：艾瑞咨询研究报告爬虫
   - 状态指示器：显示爬取状态
   - 用户区域：登录/用户信息/退出按钮
   - 操作按钮：开始爬取、刷新数据

2. **登录弹窗**
   - 手机号输入框
   - 验证码输入框
   - 获取验证码按钮（60秒倒计时）
   - 登录按钮

3. **统计面板**
   - 总报告数量
   - 已下载数量
   - 免费/付费报告数量

4. **筛选工具栏**
   - 搜索框：按标题关键词搜索（实时过滤）
   - 行业筛选：下拉多选行业分类
   - 时间筛选：快捷选项（最近一周/一月/一年）+ 自定义日期范围
   - 排序选项：发布时间/浏览量/标题 + 升序/降序
   - 重置筛选按钮

5. **报告表格**
   - 列：封面图、报告名称、发布时间、行业分类、操作
   - 每行提供：查看链接、下载按钮（未登录时禁用）
   - 支持：全选/单选、批量下载

6. **下载管理器**
   - 下载进度条
   - 当前下载任务列表
   - 下载完成提示

**技术选型：**
- UI 框架：原生 HTML + Tailwind CSS (CDN)
- 数据表格：DataTables.js 或原生实现
- HTTP 请求：Fetch API
- 状态管理：原生 JavaScript

**样式设计：**
- 整体风格：专业、简洁、商务风
- 主色调：蓝色系 (#1e40af, #3b82f6)
- 布局：响应式，支持移动端

### 4.4 一键启动脚本 (start.bat)

```batch
@echo off
chcp 65001 >nul
echo ==========================================
echo   艾瑞咨询研究报告爬虫系统
echo ==========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] Installing dependencies...
pip install -r requirements.txt -q

:: 启动服务器
echo [2/3] Starting proxy server...
start "Proxy Server" python server.py

:: 等待服务器启动
timeout /t 3 /nobreak >nul

:: 打开浏览器
echo [3/3] Opening browser...
start http://localhost:5000

echo.
echo ==========================================
echo   System started successfully!
echo   Server: http://localhost:5000
echo   Press Ctrl+C in server window to stop
echo ==========================================
```

---

## 五、数据存储方案

### 5.1 本地 JSON 存储

**数据文件：** `data/reports.json`

```json
{
  "last_updated": "2026-05-26T10:30:00",
  "total_count": 1500,
  "reports": [
    {
      "id": "freport.4822",
      "news_id": 4822,
      "title": "2026年中国宠物家居行业发展趋势白皮书",
      "cover_url": "https://pic.iresearch.cn/news/202605/639153875005635561.png",
      "detail_url": "https://report.iresearch.cn/report/202605/4822.shtml",
      "industry": "消费者洞察",
      "keywords": ["宠物家居"],
      "publish_date": "2026/5/26",
      "is_free": true,
      "downloaded": false,
      "pdf_path": null
    }
  ]
}
```

### 5.2 去重策略

- 使用 `id` 字段 (freport.{NewsId}) 作为主键去重
- 每次爬取前读取已有数据，合并时跳过已存在的记录
- 更新时间戳字段用于增量更新

---

## 六、关键功能实现细节

### 6.1 全量爬取逻辑

```
1. 读取本地已存储的数据和最后爬取的 lastId
2. 从 API 获取第一页数据 (lastId="")
3. 遍历每页数据：
   a. 检查是否已存在（去重）
   b. 调用详情 API 获取完整信息
   c. 保存到内存列表
   d. 更新 lastId 为当前页最后一条记录的 Id
4. 当返回空列表时，表示已获取全部数据
5. 合并新旧数据，保存到 JSON 文件
```

### 6.2 PDF 下载逻辑

```
1. 用户点击下载按钮
2. 前端发送请求到 /api/download/{id}
3. 后端获取报告详情，提取 PDF 下载链接
4. 使用 requests 下载 PDF 内容
5. 使用报告标题作为文件名（清理非法字符）
6. 保存到 downloads/ 目录
7. 更新下载状态
8. 返回文件或文件路径
```

### 6.3 批量下载逻辑

```
1. 用户选择多个报告（复选框）
2. 点击"批量下载"按钮
3. 前端发送 POST /api/download/batch，携带 ID 列表
4. 后端创建异步任务队列
5. 逐个下载 PDF，通过 WebSocket 或轮询返回进度
6. 可选：打包为 ZIP 后下载
```

---

## 七、错误处理与容错

### 7.1 网络错误处理

- 请求超时：设置 30 秒超时，重试 3 次
- 连接错误：指数退避重试策略
- API 限流：检测到 429 状态码时，延迟 5 秒后重试

### 7.2 数据校验

- 检查必需字段是否存在
- 验证 URL 格式
- 图片 URL 有效性检查

### 7.3 降级策略

1. API 层失败 → 自动切换到 HTML 解析层
2. HTML 解析层失败 → 切换到 Browser Use 层
3. 所有层都失败 → 记录错误，跳过该数据

---

## 八、性能优化

### 8.1 并发控制

- 使用 asyncio + aiohttp 实现异步并发
- 限制并发数：详情页请求最多 5 个并发
- 使用 semaphore 控制并发

### 8.2 缓存策略

- 本地 JSON 数据缓存
- 图片 URL 缓存（避免重复请求）
- 内存缓存热点数据

### 8.3 增量更新

- 记录最后爬取的时间戳和 lastId
- 新爬取时从上次位置继续
- 支持强制全量刷新

---

## 九、安全考虑

### 9.1 请求头伪装

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.iresearch.com.cn/',
    'Connection': 'keep-alive'
}
```

### 9.2 请求频率控制

- 单 IP 请求间隔：最小 500ms
- 随机延迟：500ms - 1500ms

---

## 十、开发步骤

### Phase 1: 基础架构 (Day 1)
1. 创建项目结构和文件
2. 实现 Flask 服务器基础框架
3. 实现第一层 API 爬取逻辑
4. 实现数据存储和去重

### Phase 2: 前端开发 (Day 2)
1. 创建 HTML 页面结构
2. 实现报告列表展示
3. 实现单个下载功能
4. 实现批量下载功能

### Phase 3: 完善功能 (Day 3)
1. 实现第二层 HTML 解析爬取
2. 实现第三层 Browser Use 爬取
3. 实现一键启动脚本
4. 测试和调试

### Phase 4: 优化和交付 (Day 4)
1. 性能优化
2. 错误处理完善
3. 文档编写
4. 最终测试

---

## 十一、依赖清单 (requirements.txt)

```
flask>=2.3.0
flask-cors>=4.0.0
requests>=2.31.0
aiohttp>=3.8.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
playwright>=1.40.0
python-dateutil>=2.8.0
```

---

## 十二、API 端点设计

| 端点 | 方法 | 描述 |
|-----|------|------|
| `/api/crawl` | GET | 触发全量爬取任务 |
| `/api/crawl/status` | GET | 获取爬取任务状态 |
| `/api/reports` | GET | 获取报告列表（支持分页、筛选） |
| `/api/reports/{id}` | GET | 获取单个报告详情 |
| `/api/download/{id}` | GET | 下载单个报告 PDF |
| `/api/download/batch` | POST | 批量下载报告 |
| `/api/stats` | GET | 获取统计数据 |
| `/api/industries` | GET | 获取行业分类列表 |
| `/api/auth/login` | POST | 发送登录验证码 |
| `/api/auth/verify` | POST | 验证验证码登录 |
| `/api/auth/logout` | POST | 退出登录 |
| `/api/auth/status` | GET | 获取登录状态 |

---

## 十三、验收标准

1. ✅ 能够成功爬取全量报告数据（标题、链接、封面图）
2. ✅ 数据去重正确，不重复爬取
3. ✅ 前端能够展示报告列表，包含封面图
4. ✅ 支持按标题关键词搜索报告
5. ✅ 支持按行业分类筛选报告
6. ✅ 支持按时间范围筛选报告
7. ✅ 支持单个 PDF 下载（需登录）
8. ✅ 支持批量 PDF 下载（需登录）
9. ✅ 支持手机号 + 验证码登录
10. ✅ 一键启动脚本能够正常启动服务器和打开浏览器
11. ✅ 代码结构清晰，有注释
12. ✅ 有基本的错误处理和日志输出

---

## 十四、风险与注意事项

1. **网站反爬**：网站可能有反爬机制，需要控制请求频率
2. **API 变更**：网站 API 可能随时变更，需要做好降级处理
3. **PDF 下载限制**：部分报告可能需要登录或付费才能下载
4. **数据量**：全量数据可能较大，需要考虑内存和存储
5. **法律合规**：仅供学习和研究使用，遵守网站的 robots.txt 和使用条款

---

## 十五、后续优化方向

1. 添加搜索和筛选功能
2. 支持按行业、时间范围筛选
3. 添加数据导出功能（Excel、CSV）
4. 支持定时自动更新
5. 添加数据可视化图表
6. 支持 PDF 内容预览

---

*文档版本: 1.0*
*创建日期: 2026-05-26*
*作者: AI Assistant*
