# 炼丹炉行业报告爬虫系统 - UI 设计方案

## 1. 设计概述

### 1.1 设计理念
- **极简主义**: 干净、专业的界面，突出数据内容
- **数据优先**: 报告封面和标题是视觉焦点
- **效率导向**: 快速访问、快速下载、快速筛选

### 1.2 色彩方案
```css
:root {
  /* 主色调 - 专业蓝 */
  --primary: #2563eb;
  --primary-dark: #1d4ed8;
  --primary-light: #dbeafe;
  
  /* 辅助色 */
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  
  /* 中性色 */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* 背景与文字 */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
}
```

### 1.3 字体规范
- **标题**: system-ui, -apple-system, "Segoe UI", sans-serif
- **正文**: system-ui, -apple-system, "Segoe UI", sans-serif
- **代码**: "SF Mono", Monaco, monospace

---

## 2. 页面布局

### 2.1 整体结构
```
┌─────────────────────────────────────────────────────────────────────┐
│  Header (固定顶部)                                                   │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  🔥 炼丹炉报告爬虫                    [刷新] [下载全部]        │ │
│  └───────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│  Toolbar (工具栏)                                                    │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  🔍 搜索报告...    排序: [发布时间▼]    视图: [卡片|列表]      │ │
│  └───────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Content Area (内容区)                                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                             │   │
│  │    卡片/列表视图展示报告数据                                  │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Footer (分页器)                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  共 64 条    <  1  2  3  4  5  ...  8  >                      │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 响应式断点
| 断点 | 宽度 | 布局 |
|------|------|------|
| Mobile | < 640px | 单列卡片 |
| Tablet | 640px - 1024px | 双列卡片 |
| Desktop | > 1024px | 四列卡片/列表 |

---

## 3. 组件设计

### 3.1 Header 组件

```html
<header class="header">
  <div class="header-left">
    <div class="logo">🔥</div>
    <h1 class="title">炼丹炉报告爬虫</h1>
    <span class="badge">v1.0</span>
  </div>
  <div class="header-right">
    <button class="btn btn-secondary">
      <span class="icon">🔄</span>
      刷新数据
    </button>
    <button class="btn btn-primary">
      <span class="icon">⬇️</span>
      下载全部
    </button>
  </div>
</header>
```

**样式规范:**
- 高度: 64px
- 背景: #ffffff
- 阴影: 0 1px 3px rgba(0,0,0,0.1)
- 左侧 Logo + 标题
- 右侧操作按钮组

### 3.2 Toolbar 组件

```html
<div class="toolbar">
  <div class="search-box">
    <span class="search-icon">🔍</span>
    <input type="text" placeholder="搜索报告标题..." />
  </div>
  
  <div class="filter-group">
    <select class="select">
      <option>发布时间</option>
      <option>浏览量</option>
      <option>标题</option>
    </select>
    
    <div class="view-toggle">
      <button class="toggle-btn active">⊞ 卡片</button>
      <button class="toggle-btn">☰ 列表</button>
    </div>
  </div>
</div>
```

**样式规范:**
- 背景: #f9fafb
- 内边距: 16px 24px
- 搜索框: 圆角8px, 宽度300px
- 筛选器: 圆角6px

### 3.3 卡片视图组件

```html
<div class="card-grid">
  <div class="report-card">
    <div class="card-image">
      <img src="cover.jpg" alt="报告封面" />
      <div class="card-overlay">
        <button class="btn-preview">👁 预览</button>
      </div>
    </div>
    <div class="card-content">
      <h3 class="card-title">健康饮料市场消费趋势洞察</h3>
      <div class="card-meta">
        <span class="date">📅 2026-03-05</span>
        <span class="views">👁 732 次浏览</span>
      </div>
    </div>
    <div class="card-actions">
      <button class="btn btn-primary btn-block">
        ⬇️ 下载 PDF
      </button>
    </div>
  </div>
</div>
```

**样式规范:**
- 卡片宽度: 280px
- 圆角: 12px
- 阴影: 0 4px 6px rgba(0,0,0,0.05)
- 悬停阴影: 0 8px 16px rgba(0,0,0,0.1)
- 封面高度: 180px
- 过渡动画: 0.2s ease

### 3.4 列表视图组件

```html
<div class="list-view">
  <div class="list-item">
    <div class="list-checkbox">
      <input type="checkbox" />
    </div>
    <div class="list-cover">
      <img src="cover.jpg" alt="封面" />
    </div>
    <div class="list-info">
      <h4 class="list-title">健康饮料市场消费趋势洞察</h4>
      <div class="list-meta">
        <span>📅 2026-03-05</span>
        <span>👁 732 次浏览</span>
        <span>🆔 HYBG20260305000</span>
      </div>
    </div>
    <div class="list-actions">
      <a href="#" class="btn-link">查看原文</a>
      <button class="btn btn-sm btn-primary">下载</button>
    </div>
  </div>
</div>
```

**样式规范:**
- 行高: 100px
- 背景: #ffffff
- 边框底部: 1px solid #e5e7eb
- 悬停背景: #f9fafb

### 3.5 分页器组件

```html
<div class="pagination">
  <span class="pagination-info">共 64 条</span>
  <div class="pagination-nav">
    <button class="page-btn" disabled>&lt;</button>
    <button class="page-btn active">1</button>
    <button class="page-btn">2</button>
    <button class="page-btn">3</button>
    <span class="page-ellipsis">...</span>
    <button class="page-btn">8</button>
    <button class="page-btn">&gt;</button>
  </div>
  <div class="pagination-size">
    <select>
      <option>20条/页</option>
      <option>50条/页</option>
      <option>100条/页</option>
    </select>
  </div>
</div>
```

---

## 4. 状态设计

### 4.1 加载状态
```html
<div class="loading-state">
  <div class="spinner"></div>
  <p>正在抓取数据...</p>
  <div class="progress-bar">
    <div class="progress-fill" style="width: 45%"></div>
  </div>
  <span class="progress-text">第 2/8 页</span>
</div>
```

### 4.2 空状态
```html
<div class="empty-state">
  <div class="empty-icon">📭</div>
  <h3>暂无数据</h3>
  <p>点击"刷新数据"按钮开始抓取报告</p>
  <button class="btn btn-primary">立即刷新</button>
</div>
```

### 4.3 错误状态
```html
<div class="error-state">
  <div class="error-icon">⚠️</div>
  <h3>数据抓取失败</h3>
  <p>网络连接异常，请稍后重试</p>
  <button class="btn btn-primary">重试</button>
</div>
```

---

## 5. 交互设计

### 5.1 按钮状态
| 状态 | 样式 |
|------|------|
| Default | 背景 #2563eb, 文字白色 |
| Hover | 背景 #1d4ed8, 轻微上移 |
| Active | 背景 #1e40af, 缩放0.98 |
| Disabled | 背景 #d1d5db, 文字 #9ca3af |
| Loading | 显示 spinner, 禁用点击 |

### 5.2 卡片交互
- **悬停**: 阴影加深, 图片轻微放大(1.05)
- **点击**: 显示下载选项
- **长按**: 多选模式

### 5.3 下载流程
```
用户点击下载
    ↓
显示下载弹窗 (文件名确认)
    ↓
显示下载进度条
    ↓
下载完成提示
    ↓
自动打开下载文件夹 (可选)
```

### 5.4 批量操作
- 列表视图支持复选框多选
- 选中后底部显示浮动操作栏
- 支持全选/取消全选

---

## 6. 动画效果

### 6.1 页面加载动画
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: fadeInUp 0.3s ease forwards;
  animation-delay: calc(var(--index) * 0.05s);
}
```

### 6.2 悬停效果
```css
.card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.15);
}
```

### 6.3 加载动画
```css
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## 7. 响应式适配

### 7.1 移动端 (< 640px)
- 单列卡片布局
- 搜索框全宽
- 底部固定操作栏
- 手势滑动切换页面

### 7.2 平板端 (640px - 1024px)
- 双列卡片布局
- 侧边栏筛选器
- 支持横竖屏切换

### 7.3 桌面端 (> 1024px)
- 四列卡片/列表布局
- 顶部工具栏
- 快捷键支持

---

## 8. 图标系统

使用 Unicode Emoji + CSS 实现，无需外部图标库：

| 功能 | 图标 | Unicode |
|------|------|---------|
| 搜索 | 🔍 | \1F50D |
| 下载 | ⬇️ | \2B07\FE0F |
| 刷新 | 🔄 | \1F504 |
| 预览 | 👁 | \1F441 |
| 日历 | 📅 | \1F4C5 |
| 浏览 | 👁 | \1F441 |
| 警告 | ⚠️ | \26A0\FE0F |
| 成功 | ✅ | \2705 |
| 错误 | ❌ | \274C |
| 文件 | 📄 | \1F4C4 |
| 文件夹 | 📁 | \1F4C1 |
| 设置 | ⚙️ | \2699\FE0F |

---

## 9. 完整 CSS 代码

见 `static/css/style.css` 文件，包含：
- CSS Variables 定义
- 所有组件样式
- 响应式媒体查询
- 动画关键帧
- 工具类

---

## 10. 设计原则总结

1. **一致性**: 统一的颜色、间距、圆角
2. **层次性**: 通过阴影和间距建立视觉层次
3. **反馈性**: 每个操作都有明确的状态反馈
4. **简洁性**: 去除多余装饰，聚焦内容
5. **可用性**: 清晰的视觉引导和操作提示
