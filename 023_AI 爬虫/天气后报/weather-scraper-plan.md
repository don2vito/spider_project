# 天气历史数据爬虫应用 - 实施计划

## 概述

构建一个完整的历史天气数据爬虫应用，包含 Python Flask 代理服务器、HTML 前端应用和一键启动脚本。目标网站为 `https://www.tianqihoubao.com/lishi/`，该网站为纯静态 HTML 页面（无 Ajax/JSON 动态加载），使用 GBK 编码，存在 User-Agent 检测和请求频率限制。

## 当前状态分析

- 目标网站结构已完整研究：省份列表 → 城市列表 → 月度数据表格
- URL 模式已确认：`/lishi/index.htm` → `/lishi/{abbr}.htm` → `/lishi/{city}/month/{YYYYMM}.html`
- 数据表格结构：4列（日期、天气状况、气温、风力风向）
- 反爬措施：UA 检测、频率限制（需 2-5s 延迟）、GBK 编码
- 无需 Selenium，使用 requests + BeautifulSoup 即可

## 项目文件结构

```
/workspace/
├── app.py              # Flask 后端代理服务器
├── index.html          # 前端单页应用（内嵌 CSS + JS）
├── start.bat           # 一键启动脚本（英文内容）
└── cache/              # 爬取数据缓存目录（自动创建）
    ├── provinces.json
    ├── cities_{abbr}.json
    └── weather_{pinyin}_{YYYYMM}.json
```

## 实施步骤

### 步骤 1：创建 `app.py` — Flask 后端代理服务器

**1.1 HTTP 请求层**
- 封装 `fetch_page(url)` 函数，设置完整浏览器请求头（User-Agent、Referer、Accept 等）
- GBK 编码处理：`response.content.decode('gbk')` 失败时 fallback 到 `gb18030`
- 请求间隔：`random.uniform(2, 5)` 秒随机延迟
- 失败重试：捕获异常后间隔 3s 重试，最多 3 次

**1.2 缓存层**
- 文件系统缓存，存储在 `cache/` 目录
- 缓存键格式：`provinces` / `cities_{abbr}` / `weather_{pinyin}_{YYYYMM}`
- TTL：省份和城市列表 7 天，天气数据 30 天

**1.3 数据解析层**
- `parse_provinces(soup)`：选择器 `#content dt a`，提取省份名称和 abbr
- `parse_cities(soup)`：DT 标签为地级市（is_main=True），DD 标签为区县
- `parse_weather(soup)`：选择器 `#content table.b tr`，提取日期/天气/气温/风力
  - 温度提取：正则 `r'(-?\d+)℃'`
  - 天气状况：按 `/` 分割白天/夜间

**1.4 API 路由**
| 路由 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 返回 index.html |
| `/api/provinces` | GET | 返回省份列表 JSON |
| `/api/cities/<abbr>` | GET | 返回某省城市列表 JSON |
| `/api/weather` | GET | 参数：year, province, cities（逗号分隔），返回天气数据 JSON |
| `/api/export` | GET | 参数同上，返回 Excel 文件下载 |

**1.5 Excel 导出**
- 使用 openpyxl 生成 xlsx 到内存（BytesIO）
- 表头：一级地区 | 二级地区 | 日期 | 白天天气 | 夜间天气 | 最高气温(℃) | 最低气温(℃) | 白天风力风向 | 夜间风力风向
- 文件名格式：`{year}_{province}_{city}.xlsx`
- 样式：深蓝表头白字、奇偶行交替色、温度负值红色

**1.6 依赖**
```
flask>=2.3.0, requests>=2.31.0, beautifulsoup4>=4.12.0, openpyxl>=3.1.0
```

### 步骤 2：创建 `index.html` — 前端单页应用

**2.1 视觉设计**
- 深色主题（气象仪表盘风格）：深蓝黑背景 `#0f172a`，卡片背景 `#1e293b`
- 强调色：琥珀金 `#f59e0b`
- 字体：系统字体栈 + 中文回退（PingFang SC, Microsoft YaHei）
- 数字/数据使用等宽字体

**2.2 三个多选下拉框**
- **年份**：范围 2011 ~ 当前年份，单选，默认当前年份
- **一级地区**：页面加载时从 `/api/provinces` 获取，单选
- **二级地区**：选中省份后从 `/api/cities/<abbr>` 获取，多选（checkbox 风格）
  - 地级市优先显示，区县折叠在下方
  - 支持搜索过滤、全选/清空

**2.3 数据表格**
- 固定表头（sticky），按年份和月份升序排列
- 多城市数据合并展示，同一日期不同城市分行
- 温度负值红色显示
- 天气图标映射（Unicode 字符：晴☀️、多云⛅、小雨🌦️ 等）
- 行悬浮高亮效果

**2.4 交互功能**
- 查询按钮：校验后逐月逐城市请求，实时更新进度条和表格
- 导出按钮：调用 `/api/export` 下载 Excel
- 加载态：骨架屏 + 进度条 + 禁用按钮
- 错误处理：Toast 提示

**2.5 动画**
- 页面加载 fadeInUp 动画
- 表格行渐入动画（staggered delay）
- 按钮悬浮上移 + 阴影效果
- 下拉框展开/收起过渡动画

### 步骤 3：创建 `start.bat` — 一键启动脚本

```bat
@echo off
chcp 65001 >nul
title Weather History Scraper
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    pause
    exit /b 1
)
echo Installing dependencies...
pip install flask requests beautifulsoup4 openpyxl -q
if not exist "cache" mkdir cache
echo Starting server...
start "" http://127.0.0.1:5000
python app.py
pause
```

- 内容使用英文
- 自动检查 Python 安装
- 自动安装依赖
- 启动服务器并打开浏览器

## 关键决策与假设

1. **纯静态爬取**：网站无 Ajax 动态加载，使用 requests + BeautifulSoup 即可，无需 Selenium
2. **文件系统缓存**：使用 JSON 文件缓存，避免重复爬取，TTL 按数据类型区分
3. **串行请求**：为避免触发反爬，所有爬取请求串行执行，间隔 2-5s
4. **分批加载**：前端逐月请求并实时更新表格，提升用户体验
5. **后端生成 Excel**：使用 openpyxl 在服务端生成 xlsx，前端触发下载
6. **年份范围**：2011 年至今（网站最早数据从 2011 年开始）
7. **未来月份处理**：后端检测月份超过当前月则跳过请求

## 验证步骤

1. 运行 `start.bat`，确认服务器启动并自动打开浏览器
2. 验证省份下拉框正确加载 34 个省级行政区
3. 选择一个省份，验证城市列表正确加载
4. 选择一个城市和年份，点击查询，验证数据表格正确展示
5. 验证数据按日期升序排列
6. 点击导出按钮，验证 Excel 文件下载成功
7. 验证 Excel 包含"一级地区"和"二级地区"字段
8. 验证文件名格式为 `年份_一级地区_二级地区.xlsx`
9. 重复查询相同数据，验证缓存生效（速度明显加快）
10. 测试边界情况：无数据月份、网络错误、大量城市选择
