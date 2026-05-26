# 验证清单

## 爬虫后端
- [x] Python 爬虫服务器能成功启动，监听 localhost:5000
- [x] 第一层（API）: POST `/Designer/Common/GetData` 成功获取全量 ≥90 条数据 — 94 条
- [x] API 层使用 session cookies 认证（无需 token），循环 5 页获取全量数据
- [x] API 层正确解析 JSON 响应字段（Id, Name, PicUrl, LinkUrl）
- [x] 第二层（Body.js）: 后备解析代码保留，Layer 1 成功时自动跳过
- [x] 第三层（Playwright）: 修正分页选择器 `li[jp-role='page'][jp-data='{N}'] a` 后可获取全量 94 条数据
- [x] 数据去重正常（基于 report id，无重复项）
- [x] `/api/reports` 返回全量报告数据（JSON 格式）
- [x] `/api/download/{report_id}` 能正确下载单个报告的图片并打包为 ZIP（75 张图片，86.5 MB）
- [x] `/api/proxy-image` 能正确代理转发图片（支持 img.wanwang.xin）
- [x] 爬取数据包含：报告标题、报告链接、封面图片 URL

## 前端 HTML 应用
- [x] HTML 页面能正确加载并展示报告表格
- [x] 表格包含：封面图片列（缩略图）、报告名称列、操作列
- [x] 封面图片通过代理接口 `/api/proxy-image` 正确显示
- [x] 单个报告下载功能正常
- [x] 勾选多条报告后批量下载功能正常
- [x] 全量下载功能正常（所有报告打包下载）
- [x] 页面有加载状态提示和空状态提示
- [x] 搜索过滤功能正常

## 一键启动
- [x] .bat 文件双击后能自动启动 Python 代理服务器
- [x] .bat 文件等待服务器启动后自动打开浏览器访问前端页面
- [x] .bat 文件与 Python 代码、HTML 文件在同一文件夹下
- [x] .bat 文件内容使用英文编写

## 文档输出
- [x] PRD 文档（.docx）包含完整的项目背景、功能需求、技术架构、接口设计
- [x] UI 方案文档（.docx）包含完整的页面布局、交互设计、组件说明
- [x] 两份文档格式规范，内容完整

## 清理
- [x] 测试文件（test_*.py）已清理 — 18 个文件已删除
