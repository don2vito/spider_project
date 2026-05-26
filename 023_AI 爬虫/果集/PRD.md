# 果集数据报告爬虫系统 - 产品需求文档 (PRD)

## 1. 项目概述

### 1.1 项目背景
果集（guoji.pro）是专业的数据分析平台，提供抖音、快手、小红书等平台的行业数据报告。用户需要一个自动化工具来批量抓取这些报告，以便离线查阅和分析。

### 1.2 项目目标
- 自动抓取果集平台全量数据报告（约384条）
- 提供可视化浏览界面
- 支持单个/批量/全量下载（PDF格式）
- 一键启动，简单易用

### 1.3 目标用户
- 数据分析师
- 市场研究人员
- 运营人员
- 对行业报告有需求的用户

---

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 数据抓取服务
| 功能 | 描述 |
|------|------|
| 列表页抓取 | 抓取32页报告列表数据 |
| 详情页抓取 | 抓取每份报告的详情页图片 |
| 数据去重 | 基于marketingId去重 |
| 缓存机制 | 内存缓存，避免重复请求 |

#### 2.1.2 三层爬取策略
| 层级 | 策略 | 说明 |
|------|------|------|
| 第一层 | API接口拦截 | 分析页面网络请求，尝试获取JSON接口 |
| 第二层 | HTML解析 | 使用BeautifulSoup解析DOM结构 |
| 第三层 | Browser Use | 使用Playwright模拟浏览器（兜底方案） |

#### 2.1.3 前端展示
| 功能 | 描述 |
|------|------|
| 数据表格 | 展示封面图片、报告名称、报告链接 |
| 搜索过滤 | 按报告名称搜索 |
| 分页显示 | 每页20条，支持翻页 |
| 全选/多选 | 支持批量选择 |

#### 2.1.4 下载功能
| 功能 | 描述 |
|------|------|
| 单个下载 | 下载单份报告为PDF |
| 批量下载 | 下载选中报告为ZIP |
| 全量下载 | 下载全部报告为ZIP |
| PDF生成 | 按图片顺序合并为PDF |

### 2.2 API接口设计

#### 2.2.1 获取报告列表
```
GET /api/reports
Response:
{
  "success": true,
  "data": [
    {
      "marketingId": "497",
      "title": "报告标题",
      "url": "https://www.guoji.pro/Report/ReportDetail?marketingId=497",
      "coverImage": "https://aka.doubaocdn.com/s/xxx"
    }
  ],
  "total": 384
}
```

#### 2.2.2 刷新数据
```
GET /api/refresh
Response: 同上
```

#### 2.2.3 获取报告详情
```
GET /api/report-detail/{marketingId}
Response:
{
  "success": true,
  "data": {
    "marketingId": "497",
    "title": "报告标题",
    "images": ["https://aka.doubaocdn.com/s/xxx", ...]
  }
}
```

#### 2.2.4 下载单个报告PDF
```
GET /api/download-pdf/{marketingId}
Response: PDF文件流
```

#### 2.2.5 批量下载
```
POST /api/download-batch
Body: { "marketingIds": ["497", "496", ...] }
Response: ZIP文件流
```

#### 2.2.6 图片代理
```
GET /api/proxy-image?url={imageUrl}
Response: 图片文件流
```

---

## 3. 技术架构

### 3.1 技术栈
| 组件 | 技术 |
|------|------|
| 后端框架 | Python Flask |
| HTTP请求 | requests |
| HTML解析 | BeautifulSoup4 |
| 图片处理 | Pillow |
| PDF生成 | Pillow (内置PDF支持) |
| 前端 | HTML + CSS + JavaScript |
| 跨域处理 | flask-cors |

### 3.2 项目结构
```
果集/
├── app.py          # Python后端服务
├── index.html      # 前端页面
├── start.bat       # 一键启动脚本
├── PRD.md          # 产品需求文档
└── UI.md           # UI方案文档
```

### 3.3 数据流图
```
用户浏览器
    ↓
index.html (前端)
    ↓ API请求
app.py (Flask服务器)
    ↓ 爬取请求
guoji.pro (目标网站)
    ↓ 返回数据
app.py (解析处理)
    ↓ JSON响应
index.html (展示)
```

### 3.4 部署架构
```
本地环境
├── Python 3.7+
├── Flask服务器 (端口5000)
└── 浏览器 (访问 localhost:5000)
```

---

## 4. 非功能需求

### 4.1 性能要求
- 首次加载时间：< 5分钟（抓取全量数据）
- 后续加载时间：< 2秒（使用缓存）
- 单个PDF生成时间：< 30秒
- 批量下载支持并发

### 4.2 可靠性要求
- 爬取失败自动重试
- 网络异常友好提示
- 数据去重保证唯一性

### 4.3 兼容性要求
- 支持Chrome、Firefox、Edge浏览器
- 支持Windows 10/11
- Python 3.7+

---

## 5. 约束与限制

### 5.1 技术约束
- 图片域名：aka.doubaocdn.com
- 需要代理图片解决跨域
- PDF生成依赖Pillow库

### 5.2 业务约束
- 遵守目标网站robots.txt
- 合理控制请求频率
- 仅供个人学习研究使用

---

## 6. 验收标准

### 6.1 功能验收
- [ ] 能成功抓取全量384条报告数据
- [ ] 前端页面正确展示表格
- [ ] 单个下载生成正确PDF
- [ ] 批量下载生成正确ZIP
- [ ] 一键启动正常工作

### 6.2 性能验收
- [ ] 首次加载完成时间 < 5分钟
- [ ] 页面响应时间 < 1秒
- [ ] PDF生成成功率达95%以上

---

## 7. 里程碑

| 阶段 | 交付物 | 状态 |
|------|--------|------|
| 阶段一 | Python爬虫服务器 | ✅ 已完成 |
| 阶段二 | HTML前端页面 | ✅ 已完成 |
| 阶段三 | 一键启动脚本 | ✅ 已完成 |
| 阶段四 | 文档输出 | ✅ 已完成 |
| 阶段五 | 测试验证 | 🔄 进行中 |
