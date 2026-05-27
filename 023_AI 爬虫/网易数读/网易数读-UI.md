# 网易数读栏目爬虫系统 - UI设计文档

## 1. 设计概述

### 1.1 设计理念
采用**现代数据工具风格**，强调：
- **专业性**：深色导航栏 + 清晰的数据展示
- **高效性**：紧凑的表格布局，快速操作
- **友好性**：圆润的边角、柔和的阴影、流畅的动效

### 1.2 设计原则
- 信息密度适中，避免视觉疲劳
- 操作反馈即时，状态变化明显
- 响应式设计，适配不同屏幕

---

## 2. 色彩系统

### 2.1 主色调
```css
:root {
  /* 主色 - 科技蓝 */
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --primary-light: #dbeafe;
  
  /* 辅助色 */
  --success: #10b981;      /* 成功绿 */
  --warning: #f59e0b;      /* 警告黄 */
  --danger: #ef4444;       /* 错误红 */
  --info: #06b6d4;         /* 信息青 */
  
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
  
  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  
  /* 文字色 */
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
}
```

### 2.2 色彩应用
| 元素 | 颜色 | 用途 |
|------|------|------|
| 顶部导航栏 | `--gray-900` | 品牌标识区 |
| 主按钮 | `--primary` | 主要操作 |
| 成功状态 | `--success` | 完成、成功提示 |
| 危险操作 | `--danger` | 删除、取消 |
| 表格边框 | `--gray-200` | 分割线 |
| 悬停背景 | `--gray-50` | 行悬停效果 |

---

## 3. 字体系统

### 3.1 字体栈
```css
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: "SF Mono", Monaco, Inconsolata, "Roboto Mono", "PingFang SC", monospace;
}
```

### 3.2 字体规格
| 级别 | 大小 | 字重 | 行高 | 用途 |
|------|------|------|------|------|
| 标题 H1 | 24px | 700 | 1.3 | 页面主标题 |
| 标题 H2 | 20px | 600 | 1.4 | 区块标题 |
| 标题 H3 | 16px | 600 | 1.5 | 卡片标题 |
| 正文大 | 16px | 400 | 1.6 | 重要正文 |
| 正文常规 | 14px | 400 | 1.6 | 默认正文 |
| 正文小 | 12px | 400 | 1.5 | 辅助文字 |
| 标签 | 12px | 500 | 1.4 | 标签、徽章 |

---

## 4. 间距系统

### 4.1 间距规格
```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
}
```

### 4.2 组件间距
| 场景 | 间距值 | 说明 |
|------|--------|------|
| 页面内边距 | `--space-6` | 容器左右边距 |
| 卡片内边距 | `--space-5` | 卡片内部间距 |
| 表单元素间距 | `--space-4` | 表单项之间 |
| 按钮内边距 | `--space-2` `--space-4` | 垂直 水平 |
| 表格行高 | 64px | 固定行高 |
| 表格单元格内边距 | `--space-3` `--space-4` | 垂直 水平 |

---

## 5. 组件设计

### 5.1 按钮 (Button)

#### 主按钮 (Primary)
```css
.btn-primary {
  background: var(--primary);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
```

#### 次按钮 (Secondary)
```css
.btn-secondary {
  background: white;
  color: var(--gray-700);
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  border: 1px solid var(--gray-300);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-secondary:hover {
  background: var(--gray-50);
  border-color: var(--gray-400);
}
```

#### 图标按钮 (Icon Button)
```css
.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-icon:hover {
  background: var(--gray-100);
}
```

### 5.2 卡片 (Card)

#### 统计卡片
```css
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--gray-200);
}
.stat-card__value {
  font-size: 32px;
  font-weight: 700;
  color: var(--primary);
  margin-top: 8px;
}
.stat-card__label {
  font-size: 14px;
  color: var(--text-secondary);
}
```

### 5.3 表格 (Table)

```css
.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
.data-table th {
  background: var(--gray-50);
  padding: 16px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  color: var(--gray-700);
  border-bottom: 1px solid var(--gray-200);
}
.data-table td {
  padding: 16px;
  border-bottom: 1px solid var(--gray-200);
  vertical-align: middle;
}
.data-table tr:hover td {
  background: var(--gray-50);
}
```

### 5.4 输入框 (Input)

```css
.input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid var(--gray-300);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}
.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
}
```

### 5.5 复选框 (Checkbox)

```css
.checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid var(--gray-300);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.checkbox:checked {
  background: var(--primary);
  border-color: var(--primary);
}
```

### 5.6 进度条 (Progress)

```css
.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--gray-200);
  border-radius: 4px;
  overflow: hidden;
}
.progress-bar__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--info));
  border-radius: 4px;
  transition: width 0.3s ease;
}
```

### 5.7 弹窗 (Modal)

```css
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal__content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  max-width: 480px;
  width: 90%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
```

### 5.8 标签 (Badge)

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
}
.badge--success {
  background: #d1fae5;
  color: #065f46;
}
.badge--warning {
  background: #fef3c7;
  color: #92400e;
}
```

---

## 6. 布局设计

### 6.1 页面结构
```
┌─────────────────────────────────────────────────────────────┐
│ Header (60px)                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Stats Section                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                       │
│  │ Card 1  │ │ Card 2  │ │ Card 3  │                       │
│  └─────────┘ └─────────┘ └─────────┘                       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Filter Bar (56px)                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Data Table                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ...                                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Pagination                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 响应式断点
| 断点 | 宽度 | 说明 |
|------|------|------|
| sm | 640px | 小屏手机 |
| md | 768px | 平板 |
| lg | 1024px | 小桌面 |
| xl | 1280px | 标准桌面 |
| 2xl | 1536px | 大屏桌面 |

---

## 7. 动效设计

### 7.1 过渡效果
```css
/* 按钮悬停 */
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

/* 弹窗出现 */
transition: opacity 0.3s ease, transform 0.3s ease;

/* 进度条 */
transition: width 0.3s ease;

/* 表格行悬停 */
transition: background-color 0.15s ease;
```

### 7.2 动画关键帧
```css
/* 加载动画 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 滑入动画 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## 8. 图标系统

### 8.1 图标来源
使用 [Lucide Icons](https://lucide.dev/) 或 [Heroicons](https://heroicons.com/)

### 8.2 图标规格
| 尺寸 | 用途 |
|------|------|
| 16px | 按钮内图标、表格操作 |
| 20px | 导航图标、表单图标 |
| 24px | 空状态、提示图标 |
| 32px | 统计卡片图标 |

### 8.3 图标列表
| 图标 | 名称 | 用途 |
|------|------|------|
| 🕷️ | Spider | 系统Logo |
| 📊 | BarChart | 数据统计 |
| 🔍 | Search | 搜索 |
| ⬇️ | Download | 下载 |
| 👁️ | Eye | 预览 |
| 🔄 | Refresh | 刷新 |
| ⚙️ | Settings | 设置 |
| ☑️ | CheckSquare | 复选框 |
| 📄 | FileText | 报告 |
| 🖼️ | Image | 图片 |

---

## 9. 空状态设计

### 9.1 无数据状态
```
┌─────────────────────────────────┐
│                                 │
│           📄                    │
│                                 │
│      暂无数据                   │
│      点击刷新按钮获取最新数据    │
│                                 │
│      [刷新数据]                 │
│                                 │
└─────────────────────────────────┘
```

### 9.2 加载状态
```
┌─────────────────────────────────┐
│                                 │
│        ⟳ 加载中...              │
│                                 │
│    [████████████████░░░] 80%   │
│                                 │
└─────────────────────────────────┘
```

### 9.3 错误状态
```
┌─────────────────────────────────┐
│                                 │
│           ⚠️                    │
│                                 │
│      获取数据失败               │
│      请检查网络连接后重试        │
│                                 │
│      [重试]                     │
│                                 │
└─────────────────────────────────┘
```

---

## 10. 交互设计

### 10.1 鼠标交互
| 操作 | 反馈 |
|------|------|
| 悬停按钮 | 背景变深、轻微上浮 |
| 悬停表格行 | 背景变浅灰 |
| 点击按钮 | 轻微缩小（scale 0.98） |
| 悬停链接 | 显示下划线 |

### 10.2 键盘交互
| 按键 | 操作 |
|------|------|
| Tab | 切换焦点 |
| Enter | 激活按钮/链接 |
| Space | 选中复选框 |
| Esc | 关闭弹窗 |
| Ctrl+A | 全选 |

### 10.3 加载状态
- 按钮加载：显示旋转图标，禁用点击
- 页面加载：显示骨架屏
- 数据加载：显示进度条

---

## 11. 实现参考

### 11.1 CSS变量完整定义
```css
:root {
  /* Colors */
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --primary-light: #dbeafe;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #06b6d4;
  
  /* Grays */
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
  
  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  
  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Microsoft YaHei", sans-serif;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
}
```

### 11.2 常用工具类
```css
/* Flex */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: 8px; }
.gap-4 { gap: 16px; }

/* Text */
.text-sm { font-size: 14px; }
.text-lg { font-size: 18px; }
.font-medium { font-weight: 500; }
.font-bold { font-weight: 700; }
.text-gray { color: var(--gray-500); }

/* Spacing */
.p-4 { padding: 16px; }
.m-4 { margin: 16px; }
.mt-2 { margin-top: 8px; }
.mb-4 { margin-bottom: 16px; }
```
