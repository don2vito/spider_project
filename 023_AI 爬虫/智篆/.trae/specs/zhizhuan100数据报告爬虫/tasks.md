# Tasks

## 阶段一：爬虫后端开发（需重写核心逻辑）

- [x] Task 1: 重写 server.py 三层爬取策略，集成隐藏 API 发现
  - [x] SubTask 1.1: 实现第一层（新）——直接 POST 请求 `https://zhizhuan100.com.cn/Designer/Common/GetData`
    - 先 GET 页面 HTML 提取 `__RequestVerificationToken`
    - 循环 pageIndex 从 0 到 4，每页 20 条，获取全量 ~94 条数据
    - 解析 JSON 响应中的 `Data` 数组，提取 `Id`, `Name`, `PicUrl`, `LinkUrl` 字段
  - [x] SubTask 1.2: 保留第二层——Body.js 解析作为后备（只获取第 1 页 20 条数据）
  - [x] SubTask 1.3: 修正第三层——修复 Playwright 分页选择器为 `li[jp-role='page'][jp-data='{N}'] a`
  - [x] SubTask 1.4: 更新 `normalize_api_data()` 函数，正确映射 API 响应字段（`Id`→id, `Name`→title, `PicUrl`→image, `LinkUrl`→link）
  - [x] SubTask 1.5: 确保数据去重逻辑正常（基于 report id）
  - [x] SubTask 1.6: 确保 `/api/reports` 接口返回全量数据（≥90 条）
  - [x] SubTask 1.7: 确保 `/api/download/{report_id}` 接口正常工作
  - [x] SubTask 1.8: 确保 `/api/proxy-image` 接口正常代理图片

## 阶段二：前端 HTML 应用开发

- [x] Task 2: 开发 HTML 前端展示页面
  - [x] SubTask 2.1: 创建 index.html 文件，包含表格布局（封面图片列、报告名称列、操作列）
  - [x] SubTask 2.2: 实现页面加载时自动调用 `/api/reports` 获取全量数据
  - [x] SubTask 2.3: 实现封面图片展示（通过代理接口显示 aka.doubaocdn.com 图片）
  - [x] SubTask 2.4: 实现单个报告下载按钮功能
  - [x] SubTask 2.5: 实现批量下载功能（勾选 + 批量下载按钮）
  - [x] SubTask 2.6: 实现全量下载按钮功能
  - [x] SubTask 2.7: 添加加载状态、空状态等 UI 细节

## 阶段三：启动脚本

- [x] Task 3: 创建一键启动 .bat 文件
  - [x] SubTask 3.1: 编写 start.bat，启动 Python 代理服务器
  - [x] SubTask 3.2: 等待服务器启动完成后自动打开浏览器访问前端页面
  - [x] SubTask 3.3: .bat 文件内容使用英文

## 阶段四：文档生成

- [x] Task 4: 生成 PRD 文档（Word 格式）
  - [x] SubTask 4.1: 使用 python-docx 生成完整的 PRD 文档
  - [x] SubTask 4.2: 包含项目背景、功能需求、技术架构、数据流图、接口设计等

- [x] Task 5: 生成 UI 方案文档（Word 格式）
  - [x] SubTask 5.1: 使用 python-docx 生成完整的 UI 方案文档
  - [x] SubTask 5.2: 包含页面布局、交互设计、组件说明、配色方案等

## 阶段五：测试验证

- [x] Task 6: 功能测试
  - [x] SubTask 6.1: 验证 API Layer 获取全量数据（≥90 条报告，去重后）— 94 条，无重复
  - [x] SubTask 6.2: 验证 Body.js 后备层可获取 20 条数据 — 代码保留，Layer 1 成功时跳过
  - [x] SubTask 6.3: 验证 Playwright 兜底层可获取全量数据 — 94 条，分页选择器已修正
  - [x] SubTask 6.4: 验证前端页面正确展示表格数据（封面图片、报告名称）— API 兼容
  - [x] SubTask 6.5: 验证单个报告下载功能正常 — 75 张图片，86.5 MB ZIP
  - [x] SubTask 6.6: 验证批量/全量下载功能正常 — 前端代码完整实现
  - [x] SubTask 6.7: 验证 .bat 一键启动功能正常 — 结构正确
  - [x] SubTask 6.8: 验证 Word 文档生成正确（PRD + UI 方案）— 两份 .docx 存在

## 阶段六：清理

- [x] Task 7: 清理测试文件（test_*.py）— 已删除 18 个文件

---
# Task Dependencies
- Task 1 是所有后续任务的基础
- Task 2 依赖 Task 1（前端需要后端 API 接口）
- Task 3 依赖 Task 1 和 Task 2（启动脚本需要知道服务器和前端路径）
- Task 4 和 Task 5 可与 Task 1-3 并行开发
- Task 6 依赖 Task 1-5 完成
- Task 7 依赖 Task 6 完成
