# 巨潮资讯网公告爬虫 + HTML 应用 实现计划

## 一、任务理解

### 目标
构建一个完整的系统，包含：
1. **Python 代理服务器** — 爬取巨潮资讯网 (cninfo.com.cn) 公告数据
2. **HTML 前端应用** — 提供筛选、展示、排序、下载功能

### 核心需求
- 用户通过日历控件自由选择日期范围，抓取该时间段内全量公告数据（代码、简称、标题、链接、时间）
- 前端支持按公告类别筛选（年报、半年报、一季报、三季报等）
- 表格支持按公告时间和简称自定义升降序排序
- 每行提供单条下载按钮（PDF）
- 表格上方提供"下载全部"按钮

### 技术约束
- 跨域限制：浏览器无法直接请求 cninfo.com.cn API，需要 Python 代理服务器中转
- 反爬措施：需模拟浏览器请求头、Cookie 会话、请求频率控制（2-5秒间隔）
- 全量数据：需循环分页爬取所有页的数据

---

## 二、技术方案

### 架构设计

```
┌─────────────────┐         ┌──────────────────────┐         ┌──────────────────┐
│   HTML 前端应用  │  HTTP   │  Python Flask 代理    │  HTTPS  │  cninfo.com.cn   │
│   (浏览器)       │ ◄─────► │  服务器 (localhost)    │ ◄─────► │  API 接口         │
│                  │  JSON   │                      │  POST   │                  │
│  - 筛选条件      │         │  - /api/search        │         │  /new/hisAnnoun-  │
│  - 数据表格      │         │  - /api/download      │         │  cement/query     │
│  - 排序/下载     │         │  - /api/download-all  │         │                  │
└─────────────────┘         └──────────────────────┘         └──────────────────┘
```

### 技术栈
| 组件 | 技术选型 | 理由 |
|------|---------|------|
| 后端代理 | Python + Flask | 轻量、易部署、requests 库处理 HTTP |
| 前端应用 | 单文件 HTML + Tailwind CSS + 原生 JS | 无需构建、双击即可运行、设计精美 |
| 数据通信 | REST API (JSON) | 前后端分离、标准接口 |

---

## 三、实现步骤

### Step 1: 创建 Python 代理服务器 (`server.py`)

**文件**: `/workspace/server.py`

**功能模块**:

#### 1.1 会话管理
- 使用 `requests.Session()` 维持 Cookie 会话
- 首次启动时访问 `https://www.cninfo.com.cn/` 获取初始 Cookie
- 设置完整的浏览器请求头（User-Agent、Referer、X-Requested-With 等）

#### 1.2 API 接口 `/api/search` (POST)
- 接收前端参数：
  - `stock`（代码/简称/拼音，对应 cninfo 的 `stock` 参数）
  - `searchkey`（标题关键字，对应 cninfo 的 `searchkey` 参数）
  - `plate`（板块，对应 cninfo 的 `plate` 参数）
  - `trade`（行业，对应 cninfo 的 `trade` 参数，多个用分号分隔）
  - `category`（公告类别，对应 cninfo 的 `category` 参数）
  - `date_start`、`date_end`（日期范围，拼接为 `seDate` 参数）
- 构造 cninfo API 请求 payload
- 循环分页获取全量数据（pageSize=100，自动翻页直到 hasMore=false）
- 每次请求间隔 2-3 秒，防止频率限制
- 实现指数退避重试机制（失败后等待 2s→4s→8s，最多3次）
- 返回 JSON：`{ total, data: [{secCode, secName, title, time, pdfUrl, adjunctSize}] }`

#### 1.3 API 接口 `/api/download` (GET)
- 接收参数：`pdf_url`（PDF 完整 URL）
- 代理下载 PDF 文件流
- 设置正确的 Content-Disposition 响应头，触发浏览器下载

#### 1.4 API 接口 `/api/download-all` (POST)
- 接收参数：`files: [{filename, url}]`（文件列表）
- 逐个下载 PDF 并打包为 ZIP 文件
- 返回 ZIP 文件流供前端下载
- 使用 Python `zipfile` 模块在内存中打包

#### 1.5 启动配置
- 默认监听 `http://localhost:5000`
- 启用 CORS（`flask-cors`）允许前端跨域访问
- 提供清晰的启动日志提示

### Step 2: 创建 HTML 前端应用 (`index.html`)

**文件**: `/workspace/index.html`

#### 2.1 设计风格
- **美学方向**: 现代金融数据仪表盘风格，深色主题 + 蓝色强调色
- **字体**: 使用 Noto Sans SC（中文）+ JetBrains Mono（数据/代码）
- **色彩**: 深灰背景 (#0f1117) + 卡片 (#1a1d27) + 蓝色强调 (#3b82f6) + 绿色成功 (#10b981)
- **动效**: 加载动画、行悬停高亮、按钮微交互、数据渐入效果

#### 2.2 筛选区域（顶部）
布局参照 cninfo.com.cn 原站搜索面板，采用 2 列网格布局：

**第一行 — 搜索输入框（2列并排）：**
- **代码/简称/拼音**: 文本输入框，支持按股票代码、简称或拼音搜索特定公司
- **标题关键字**: 文本输入框，支持按公告标题关键字模糊搜索

**第二行 — 下拉选择器（2列并排）：**
- **板块**: 单选下拉菜单（深沪、沪市、深市、创业板、科创板、北交所）
- **行业**: 多选下拉面板（展开后为3列复选框网格），包含19个行业分类：
  - 农林牧渔业、采矿业、制造业、电力热力燃气及水、建筑业、批发和零售业、交通运输仓储和邮政业、住宿和餐饮业、信息传输软件和信息技术服务业、金融业、房地产业、租赁和商务服务业、科学研究和技术服务业、水利环境和公共设施管理业、居民服务修理和其他服务业、教育、卫生和社会工作、文化体育和娱乐业、综合

**第三行 — 日期范围：**
- **日期范围**: 日历控件（开始日期 + 结束日期），用户自由点选任意时间段，默认为空（用户必须选择后才能查询）

**第四行 — 公告类别 + 查询按钮：**
- **公告类别**: 复选框按钮组（年报、半年报、一季报、三季报、业绩预告、权益分派、董事会、监事会、股东大会等）
- **查询按钮**: 蓝色主按钮，点击后触发数据抓取

#### 2.3 数据表格区域
- **统计栏**: 显示"共 X 条结果"、当前筛选条件摘要
- **排序控件**: 公告时间（升序/降序）、简称（升序/降序）切换按钮
- **表格列**:
  | 列 | 说明 |
  |----|------|
  | 序号 | 自动编号 |
  | 证券代码 | secCode |
  | 证券简称 | secName |
  | 公告标题 | announcementTitle（可点击跳转原文） |
  | 公告时间 | 格式化日期 YYYY-MM-DD HH:MM |
  | 附件大小 | 格式化 KB/MB |
  | 操作 | 下载按钮 |

#### 2.4 下载功能
- **单条下载**: 每行"下载"按钮 → 调用 `/api/download?url=xxx`
- **下载全部**: 表格上方"下载全部"按钮 → 收集所有 PDF URL → 调用 `/api/download-all` → 下载 ZIP
- **下载进度**: 显示下载进度条和状态文字

#### 2.5 交互体验
- 加载状态：骨架屏 + 进度提示（正在抓取第 X/Y 页...）
- 空状态：无数据时显示友好提示
- 错误处理：网络错误、频率限制等场景的友好提示
- 响应式设计：适配不同屏幕宽度

### Step 3: 创建依赖文件 (`requirements.txt`)

**文件**: `/workspace/requirements.txt`

```
flask>=3.0
flask-cors>=4.0
requests>=2.31
```

### Step 4: 创建启动脚本 (`start.bat` / `start.sh`)

提供一键启动脚本，自动安装依赖并启动服务器 + 打开浏览器。

---

## 四、API 参数映射表

### 公告类别代码
| 中文 | category 值 |
|------|-------------|
| 年报 | `category_ndbg_szsh` |
| 半年报 | `category_bndbg_szsh` |
| 一季报 | `category_yjdbg_szsh` |
| 三季报 | `category_sjdbg_szsh` |
| 业绩预告 | `category_yjygjxz_szsh` |
| 权益分派 | `category_qyfpxzcs_szsh` |
| 董事会公告 | `category_dshgg_szsh` |
| 监事会公告 | `category_jshgg_szsh` |
| 股东大会 | `category_gddh_szsh` |
| 日常经营 | `category_rcjy_szsh` |
| 公司治理 | `category_gszl_szsh` |
| 中介报告 | `category_zj_szsh` |
| 首发 | `category_sf_szsh` |
| 增发 | `category_zf_szsh` |
| 股权激励 | `category_gqjl_szsh` |
| 配股 | `category_pg_szsh` |
| 解禁 | `category_jj_szsh` |
| 公司债 | `category_gszq_szsh` |
| 可转债 | `category_kzzq_szsh` |
| 其他融资 | `category_qtrz_szsh` |
| 股权变动 | `category_gqbd_szsh` |
| 补充更正 | `category_bcgz_szsh` |
| 澄清致歉 | `category_cqdq_szsh` |
| 风险提示 | `category_fxts_szsh` |
| 特别处理和退市 | `category_tbclts_szsh` |
| 退市整理期 | `category_tszlq_szsh` |

### 板块代码
| 中文 | plate 值 |
|------|----------|
| 深沪（全部） | `''`（空） |
| 深市 | `sz` |
| 深主板 | `szmb` |
| 创业板 | `szcy` |
| 沪市 | `sh` |
| 沪主板 | `shmb` |
| 科创板 | `shkcp` |
| 北交所 | `bj` |

### 行业代码（trade 参数）
| 中文 | trade 值 |
|------|-----------|
| 农、林、牧、渔业 | `A01` |
| 采矿业 | `B01` |
| 制造业 | `C01` |
| 电力、热力、燃气及水生产和供应业 | `D01` |
| 建筑业 | `E01` |
| 批发和零售业 | `F01` |
| 交通运输、仓储和邮政业 | `G01` |
| 住宿和餐饮业 | `H01` |
| 信息传输、软件和信息技术服务业 | `I01` |
| 金融业 | `J01` |
| 房地产业 | `K01` |
| 租赁和商务服务业 | `L01` |
| 科学研究和技术服务业 | `M01` |
| 水利、环境和公共设施管理业 | `N01` |
| 居民服务、修理和其他服务业 | `O01` |
| 教育 | `P01` |
| 卫生和社会工作 | `Q01` |
| 文化、体育和娱乐业 | `R01` |
| 综合 | `S01` |

> 注：行业代码需在实现时通过浏览器 F12 抓包确认实际值，上述为证监会行业分类标准编码，可能与 cninfo 实际使用的值有差异。

---

## 五、关键实现细节

### 5.1 全量数据爬取逻辑
```python
all_data = []
page = 1
while True:
    payload['pageNum'] = str(page)
    resp = session.post(API_URL, headers=headers, data=payload)
    result = resp.json()
    all_data.extend(result['announcements'])
    if not result['hasMore']:
        break
    page += 1
    time.sleep(random.uniform(2, 4))  # 随机延迟防反爬
```

### 5.2 反爬策略
- 使用 `requests.Session()` 自动管理 Cookie
- 请求间隔 2-4 秒（随机化）
- 指数退避重试（2s → 4s → 8s）
- 完整浏览器请求头模拟
- 首次请求前访问首页获取 Session Cookie

### 5.3 PDF 下载代理
```python
@app.route('/api/download')
def download():
    url = request.args.get('url')
    resp = session.get(url, stream=True)
    filename = url.split('/')[-1]
    return Response(resp.iter_content(chunk_size=8192),
                    headers={'Content-Disposition': f'attachment; filename={filename}'})
```

### 5.4 ZIP 打包下载全部
```python
@app.route('/api/download-all', methods=['POST'])
def download_all():
    files = request.json['files']
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for f in files:
            resp = session.get(f['url'])
            zf.writestr(f['filename'], resp.content)
    zip_buffer.seek(0)
    return Response(zip_buffer, mimetype='application/zip',
                    headers={'Content-Disposition': 'attachment; filename=announcements.zip'})
```

---

## 六、文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| Python 代理服务器 | `/workspace/server.py` | Flask 后端，API 代理 + 数据爬取 |
| HTML 前端应用 | `/workspace/index.html` | 单文件前端，筛选 + 表格 + 下载 |
| 依赖文件 | `/workspace/requirements.txt` | Python 依赖包列表 |
| 启动脚本 | `/workspace/start.sh` | Linux/Mac 一键启动脚本 |
| 启动脚本 | `/workspace/start.bat` | Windows 一键启动脚本 |

---

## 七、使用流程

1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务器：`python server.py`
3. 浏览器打开：`http://localhost:5000`（自动打开 index.html）
4. 选择筛选条件（日期范围、板块、公告类别）
5. 点击"查询"按钮，等待数据抓取完成
6. 在表格中查看数据，支持排序
7. 单条下载或"下载全部"ZIP

---

## 八、验证步骤

1. 启动服务器，确认无报错
2. 打开浏览器访问 `http://localhost:5000`
3. 选择"年报"类别，通过日历控件选择一个日期范围（如最近7天）
4. 点击查询，确认数据正常加载
5. 测试排序功能（时间升序/降序、简称升序/降序）
6. 测试单条 PDF 下载
7. 测试"下载全部"ZIP 下载
8. 测试不同板块和类别组合
9. 测试边界情况（无数据、网络错误）
