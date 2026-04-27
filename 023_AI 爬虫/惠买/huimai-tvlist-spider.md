# 惠买网(www.huimai.com.cn/tvList) 节目表爬虫开发计划

## 任务理解

**目标**：编写Python爬虫代码，获取"优购物"和"爱家购物"两个频道每天的电视购物节目表信息。

**输出**：一个完整的Python爬虫脚本文件 `huimai_tvlist_spider.py`

---

## 网站技术分析结果

### 数据加载方式

该页面采用**服务端渲染 + Ajax动态加载**混合模式：

1. **初始加载**：页面HTML中直接嵌入了当天（今日）的节目数据（以JSON形式嵌入在 `renderGoodsLayer()` 函数调用中）
2. **切换频道/日期**：通过Ajax POST请求 `/getTvList` 接口获取数据

### 关键API接口

| 项目 | 值 |
|------|-----|
| **接口URL** | `https://www.huimai.com.cn/getTvList` |
| **请求方法** | POST |
| **请求参数** | `channel`（频道key）+ `date`（Unix时间戳，当天0点） |
| **Content-Type** | `application/x-www-form-urlencoded` |
| **必需Headers** | `Referer: https://www.huimai.com.cn/tvList` |

### 频道标识

| 频道名称 | channel参数 | 说明 |
|----------|------------|------|
| 优购物 | `UGO1` | 优购物节目表 |
| 爱家购物 | `BTV1` | 爱家购物节目表 |

### 日期参数

- `date` 参数为Unix时间戳（秒），对应日期的00:00:00
- 例如：`2026-04-24` → `1776960000`
- 页面提供最近7天的日期选择

### 返回数据结构

```json
{
  "code": 0,
  "msg": "",
  "data": {
    "clickTime": "1776960000",
    "date": "2026-04-24",
    "displayNum": 3,
    "tvItemList": [
      [
        {
          "begin": "00:00",
          "end": "00:39",
          "beginTime": "1776960000",
          "endTime": "1776962399",
          "goodsId": "876256",
          "goodsName": "Healthwow多维营养蛋白粉优选组",
          "price": "479",
          "shopPrice": "599",
          "mainPicUrl": "https://...",
          "actLabelDesc": "限时降价",
          "channelKey": "UGO1",
          "channelName": "优购物",
          "isLiving": "1",
          "isCurrent": "0",
          ...
        }
      ],
      ...
    ]
  }
}
```

- `tvItemList` 是一个二维数组，每个子数组包含一个商品对象
- 每个时间段对应一个商品

---

## 实施方案

### 创建文件：`/workspace/huimai_tvlist_spider.py`

### 代码结构设计

```
huimai_tvlist_spider.py
├── 导入依赖（requests, json, datetime, time, csv）
├── 常量定义
│   ├── BASE_URL = "https://www.huimai.com.cn"
│   ├── API_URL = "/getTvList"
│   ├── CHANNELS = {"UGO1": "优购物", "BTV1": "爱家购物"}
│   └── HEADERS（含Referer、User-Agent等）
├── 工具函数
│   ├── date_to_timestamp(date_str) - 日期字符串转Unix时间戳
│   ├── timestamp_to_date(ts) - 时间戳转日期字符串
│   └── get_date_range(days) - 获取最近N天的日期列表
├── 核心函数
│   ├── fetch_tvlist(channel, date_timestamp) - 调用API获取单日单频道节目表
│   ├── parse_tvlist(response_data) - 解析API返回的JSON数据
│   └── crawl_all(channel, days) - 爬取指定频道最近N天的节目表
├── 输出函数
│   ├── print_table(data) - 格式化打印节目表
│   └── save_to_csv(data, filename) - 保存为CSV文件
└── main() - 主入口，爬取两个频道数据并输出
```

### 关键实现细节

1. **请求构造**：
   - 使用 `requests.Session()` 保持会话
   - 设置 `Referer` 和 `User-Agent` 请求头
   - POST请求，参数为 `channel` 和 `date`

2. **日期处理**：
   - 使用Python `datetime` 模块生成日期
   - 转换为Unix时间戳（东八区 UTC+8）
   - 默认获取最近7天数据

3. **数据提取**（从每个商品对象中提取）：
   - `begin` / `end`：节目时间段
   - `goodsName`：商品名称
   - `price`：售价
   - `shopPrice`：原价/平日价
   - `goodsId`：商品ID
   - `actLabelDesc`：活动标签（如"限时降价"、"有赠品"）
   - `isLiving`：是否正在直播
   - `mainPicUrl`：商品图片

4. **输出格式**：
   - 控制台表格打印
   - CSV文件导出

5. **容错处理**：
   - 请求超时重试
   - 异常捕获和日志
   - 空数据处理

---

## 验证步骤

1. 运行爬虫脚本，确认能成功获取优购物(UGO1)和爱家购物(BTV1)的节目表
2. 验证返回数据包含完整字段（时间、商品名、价格等）
3. 验证CSV文件正确生成
4. 验证不同日期的数据获取正常
