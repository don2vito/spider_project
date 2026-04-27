# 第一展会网(onezh.com) 2026年展会信息爬虫 - 实施计划

## 任务理解

**目标**：编写Python爬虫，从 `https://www.onezh.com/zhanhui/` 爬取2026年国内每月展会信息，按"上海"和"非上海"分类输出。

**输出**：一个Python爬虫脚本文件 `onezh_spider.py`，保存到 `/workspace/`。

---

## 网站结构分析（已完成研究）

### URL模式
月份链接格式：`/zhanhui/{page}_{region}_{industry}_{category}_{start_date}/{end_date}/`

- `{page}`: 页码（第1页为1，第2页为2...）
- `{region}`: 地区筛选（0=不限，21=上海，其他省份有对应编号）
- `{industry}`: 行业筛选（0=不限）
- `{category}`: 分类（0=不限）
- `{start_date}` / `{end_date}`: 日期范围，格式 `YYYYMMDD`

**12个月份URL示例**：
| 月份 | URL |
|------|-----|
| 1月 | `/zhanhui/1_0_0_0_20260101/20260131/` |
| 2月 | `/zhanhui/1_0_0_0_20260201/20260228/` |
| 3月 | `/zhanhui/1_0_0_0_20260301/20260331/` |
| ... | ... |
| 12月 | `/zhanhui/1_0_0_0_20261201/20261231/` |

### 分页机制
- **服务端渲染**（SSR），非Ajax/JSON动态加载
- 分页通过URL中第一个数字控制：`/zhanhui/{page}_0_0_0_{start}/{end}/`
- 尾页链接格式：`/zhanhui/{total_pages}_0_0_0_{start}/{end}/`
- 分页HTML位于 `<div class="Page"><div class="NewPage">` 中
- 尾页`<a>`标签包含总页数信息，也可从 `<span>共{N}页</span>` 提取

### 展会列表HTML结构
每个展会条目位于 `<div class='row'>` 中：
```html
<div class='row'>
  <a href='/web/index_XXXXX.html' target='_blank' title='展会名称'>
    <img src='...' width='110' height='70' alt='展会名称' />
  </a>
  <div class='info '>
    <dl>
      <dd>
        <strong><a href='/web/index_XXXXX.html'>展会名称</a></strong>
        <span class='baomingcanzhang'>参展</span>  <!-- 可选标签 -->
      </dd>
      <dd>
        <div class='mark_1'>
          <div class='area'>面积：60000㎡</div>
          <div class='people1'>参商：800+</div>
          <div class='people2'>观众：40000+</div>
        </div>
        <div class='cont'>
          <em class='cgree1'>展会简介...</em>
          <em class='cgree1'><br>展会时间：2026年03月29日—03月31日&nbsp;&nbsp;展馆：<a href='...'>展馆名称</a></em>
        </div>
      </dd>
    </dl>
  </div>
</div>
```

### 需提取的字段
| 字段 | 提取方式 |
|------|---------|
| 展会名称 | `<div class='row'>` 内 `<strong><a>` 的 `title` 属性或文本 |
| 展会详情链接 | `<div class='row'>` 内 `<strong><a>` 的 `href` |
| 展会时间 | `<em class='cgree1'>` 中 `展会时间：...` |
| 展馆名称 | `<em class='cgree1'>` 中 `展馆：` 后的文本 |
| 展会面积 | `<div class='area'>` 文本（可选） |
| 参商数量 | `<div class='people1'>` 文本（可选） |
| 观众数量 | `<div class='people2'>` 文本（可选） |
| 展会简介 | 第一个 `<em class='cgree1'>` 的文本 |

### 上海判断逻辑
展馆名称中包含"上海"关键词即判定为上海展会。常见上海展馆：
- 上海新国际博览中心、国家会展中心（上海）、上海世博展览馆、上海跨国采购会展中心、上海汽车会展中心、上海世贸商城展馆等

---

## 实施方案

### 技术选型
- **requests** + **BeautifulSoup4**（纯服务端渲染，无需Selenium/Playwright）
- **pandas**（数据整理和Excel导出）
- **time.sleep**（请求间隔，礼貌爬取）
- **re**（正则提取时间等信息）

### 爬虫逻辑
1. 定义12个月的URL模板
2. 对每个月份：
   a. 请求第1页
   b. 解析展会列表 `<div class='row'>`
   c. 从分页区域获取总页数
   d. 循环请求第2页到最后一页
   e. 每页解析并提取展会信息
3. 按展馆名称是否包含"上海"分类
4. 输出为Excel文件（两个Sheet：上海/非上海）

### 反爬策略
- 设置合理的 `User-Agent`
- 请求间隔 1-2 秒
- 使用 `requests.Session()` 复用连接

### 输出格式
- Excel文件 `2026年展会信息.xlsx`
  - Sheet 1: "上海展会" — 所有展馆在上海的展会
  - Sheet 2: "非上海展会" — 展馆不在上海的展会
- 每条记录包含：月份、展会名称、展会时间、展馆名称、展会面积、参商数、观众数、简介、详情链接

---

## 实施步骤

### Step 1: 创建爬虫脚本
- 文件：`/workspace/onezh_spider.py`
- 包含完整的爬虫逻辑、数据解析、Excel导出功能

### Step 2: 验证脚本
- 运行脚本，确认能正确爬取数据
- 检查输出Excel文件格式和内容

---

## 假设与决策
1. **无需登录**：公开页面无需认证即可访问
2. **纯SSR**：已确认页面为服务端渲染，无需处理Ajax/JSON
3. **上海判断**：基于展馆名称中是否包含"上海"关键词
4. **输出格式**：Excel (.xlsx)，含两个Sheet
5. **依赖库**：requests, beautifulsoup4, pandas, openpyxl
