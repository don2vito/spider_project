# 电子教材全量抓取工具 - 实施计划

## 摘要

针对国家中小学智慧教育平台（`https://basic.smartedu.cn/tchMaterial`）的电子教材数据，开发一个**Python代理服务器 + HTML前端应用 + Windows一键启动脚本**的完整解决方案。实现教材分类筛选、全量数据展示、自定义排序、单个/批量PDF下载功能。

## 当前状态分析

### 目标网站技术架构
- **数据加载方式**：页面初始化时并行加载4个静态JSON分片文件（`part_100.json` ~ `part_103.json`），所有筛选在前端完成
- **无需登录**：JSON数据和PDF文件均可公开访问
- **PDF获取方式**：列表JSON中无PDF链接，需通过详情API（`/details/{contentId}.json`）获取，从`ti_items`中提取`ti_is_source_file=true`的条目
- **PDF CDN**：`c1.ykt.cbern.com.cn` 公开可访问，无需认证

### 已验证的关键API
| 用途 | URL |
|------|-----|
| 版本控制 | `https://s-file-2.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/version/data_version.json` |
| 教材列表(4个分片) | `https://s-file-{1,2}.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/part_{100-103}.json` |
| 教材详情 | `https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/details/{contentId}.json` |
| PDF下载 | `https://c1.ykt.cbern.com.cn/edu_product/esp/assets/{id}.pkg/{filename}.pdf` |

### 筛选维度（tag_dimension_id）
| 维度ID | 名称 | 示例值 |
|--------|------|--------|
| `zxxxd` | 学段 | 小学、初中、高中、特殊教育等 |
| `zxxxk` | 学科 | 道德与法治、语文、数学、英语等 |
| `zxxbb` | 版本 | 统编版、人教版等 |
| `zxxnj` | 年级 | 一年级~九年级等 |
| `zxxcc` | 册别 | 上册、下册、全一册 |

## 项目文件结构

```
/workspace/textbook-scraper/
├── server.py      # Python Flask 代理服务器
├── index.html     # 前端页面（单文件，内嵌CSS/JS）
└── start.bat      # Windows 一键启动脚本
```

## 实施方案

### 文件1: `server.py` - Python代理服务器

**技术选型**：Flask + requests（仅两个第三方依赖）

**API端点设计**：

| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| GET | `/` | 返回index.html | 无 |
| GET | `/api/filters` | 获取所有筛选维度及选项 | 无 |
| GET | `/api/textbooks` | 获取筛选后的教材列表 | `xd`,`xk`,`bb`,`nj`,`cc`（逗号分隔，可选） |
| GET | `/api/pdf-url/<content_id>` | 获取教材PDF下载URL | path参数 |
| GET | `/api/download/<content_id>` | 代理下载PDF文件（流式） | path参数 |

**核心实现要点**：

1. **数据加载与缓存**
   - 启动时用`threading`并行请求4个分片JSON，合并到内存缓存
   - 从`tag_list`提取所有唯一筛选选项，按`order_num`排序
   - PDF URL按需获取并缓存（首次下载时请求详情API）

2. **筛选逻辑**
   - 维度间AND关系，同维度内多选OR关系
   - 从缓存的全部教材中过滤，返回匹配结果

3. **PDF下载代理**
   - 先查PDF URL缓存，未命中则请求详情API提取
   - 从`ti_items`中找`ti_is_source_file=true`的条目
   - 将`ti_storages`中的`-ndr-private`域名替换为`c1.ykt.cbern.com.cn`
   - 使用`stream=True`流式传输，避免大文件内存溢出
   - 中文文件名使用`filename*=UTF-8''`编码

4. **启动配置**
   - `host="127.0.0.1"`, `port=5000`
   - 启动时预加载数据并打印加载数量

### 文件2: `index.html` - 前端页面

**技术方案**：纯HTML + 内嵌CSS + 内嵌JavaScript，无框架依赖

**页面布局**：
```
┌──────────────────────────────────────────────┐
│  标题: 电子教材下载工具                         │
├──────────────────────────────────────────────┤
│  筛选区域: [学段▼] [学科▼] [版本▼] [年级▼] [册别▼] │
│  [清除筛选]                                    │
├──────────────────────────────────────────────┤
│  共N条 | 排序: 标题▲/▼ | [下载全部]             │
├──────────────────────────────────────────────┤
│  表格: 序号|标题|学段|学科|版本|年级|册别|大小|出版社|操作│
│  每行末尾: [下载] 按钮                          │
└──────────────────────────────────────────────┘
```

**核心功能**：

1. **多选下拉筛选器**
   - 5个维度各一个多选下拉菜单
   - 支持"全选/取消全选"
   - 选中后显示已选数量（如"学段 (2)"）
   - 任何筛选变化自动刷新列表

2. **结果表格**
   - 列：序号、标题、学段、学科、版本、年级、册别、大小（MB）、出版社、操作
   - 标题列支持升降序切换（中文拼音排序`localeCompare("zh-CN")`）
   - 斑马纹、hover高亮、固定表头

3. **下载功能**
   - 单个下载：点击行末"下载"按钮，通过代理下载PDF
   - 全部下载：逐个触发下载，显示进度（"正在下载 3/50..."），间隔500ms
   - 下载状态反馈：loading → done / error

4. **UI设计**（遵循frontend-design Skill）
   - 配色：蓝色主色调（`#2563EB`），灰色背景，白色卡片
   - 字体：`"PingFang SC", "Microsoft YaHei", sans-serif`
   - 加载状态：CSS spinner + 半透明遮罩
   - 响应式：表格水平可滚动，筛选器自动换行

### 文件3: `start.bat` - Windows启动脚本

**功能**：
1. 检查Python是否安装
2. 自动安装依赖（`flask requests`）
3. 启动Python服务器（后台运行）
4. 等待3秒后自动打开浏览器
5. 脚本内容使用英文

## 假设与决策

1. **无需登录**：已验证公开CDN可直接访问PDF，不实现登录功能
2. **数据量可控**：约1000-2000条教材记录，前端直接DOM渲染，无需虚拟滚动
3. **平铺筛选**：5个维度同时显示全部选项，不做级联（简化实现，空结果时提示调整）
4. **PDF URL懒加载**：不在列表加载时批量获取PDF URL，而是在用户点击下载时按需获取并缓存
5. **单文件前端**：HTML/CSS/JS全部内嵌在一个文件中，便于分发

## 验证步骤

1. **启动验证**：运行`start.bat`，确认服务器启动且浏览器自动打开
2. **数据加载验证**：页面打开后筛选选项正确显示，教材列表完整加载
3. **筛选验证**：选择不同维度组合，结果正确过滤
4. **排序验证**：点击标题列头，升降序切换正确
5. **单个下载验证**：点击某条教材的下载按钮，PDF文件正确下载
6. **批量下载验证**：点击"下载全部"，所有PDF逐个下载，进度显示正确
7. **边界测试**：空筛选结果提示、特殊字符文件名、大文件（50MB+）下载
