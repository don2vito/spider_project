# 环球购物（聚鲨环球精选）节目表爬虫开发计划

## 摘要

通过逆向分析 `https://wp.sharkshopping.com/programs_list` 网页，发现其节目数据通过Ajax请求从后端API获取。本计划将基于发现的3个核心API接口，使用Python编写一个完整的爬虫脚本，获取环球购物每天的节目表信息。

## 当前状态分析

### 网页技术架构
- **前端框架**：Vue.js（SPA单页应用）
- **数据加载方式**：Ajax/XHR 动态请求，非服务端渲染
- **API基础地址**：`https://api.sharkshopping.com/ec/api`
- **签名机制**：每个请求需要 `timestamp` 和 `sign` 参数（MD5签名）

### 已发现的3个核心API接口

#### 1. 获取可查询日期列表
- **接口**：`method=tv.program.date`
- **URL**：`https://api.sharkshopping.com/ec/api?method=tv.program.date&appid=webapp&token=&version=4.4.1&source=wap&city_num=310100&oriSource=wap&timestamp={ts}&sign={sign}`
- **返回**：日期数组，包含 `show_date`（显示日期）和 `real_date`（实际日期 YYYY-MM-DD）
- **示例**：`[{"show_date":"今日","real_date":"2026-04-24"}, ...]`

#### 2. 获取节目分类列表
- **接口**：`method=tv.program.categories`
- **URL**：`https://api.sharkshopping.com/ec/api?method=tv.program.categories&appid=webapp&token=&version=4.2.0&source=wap&city_num=310100&oriSource=wap&timestamp={ts}&sign={sign}`
- **返回**：分类及品牌列表

#### 3. 获取节目数据（核心接口）
- **接口**：`method=tv.program.data`
- **URL**：`https://api.sharkshopping.com/ec/api?method=tv.program.data&appid=webapp&token=&version=4.4.1&source=wap&city_num=310100&brand_id=&date=2026-04-24&cat_id=&oriSource=wap&timestamp={ts}&sign={sign}`
- **参数**：
  - `date`：查询日期（YYYY-MM-DD格式）
  - `cat_id`：分类ID（可选，为空查全部）
  - `brand_id`：品牌ID（可选，为空查全部）
  - `city_num`：城市编号（默认310100=上海）
- **返回数据结构**：
  ```json
  {
    "rsp": "succ",
    "data": {
      "returndata": {
        "channel": {"channel_name": "聚鲨环球精选", "tv_id": "1000001"},
        "program_data": [
          {
            "show_date": "4月24日",
            "real_date": "2026-04-24",
            "start_time": 1776960000,    // Unix时间戳
            "end_time": 1776962400,      // Unix时间戳
            "cat_name": "滋补养生",
            "brand_name": "其他",
            "goods": {
              "sku": "97094021",
              "name": "御寿堂加拿大西洋参切片",
              "price": "369",
              "marketprice": "399",
              "image": "http://...",
              "description": "立减30",
              "wapUrl": "http://wp.sharkshopping.com/product/97094021",
              "product_first": "保健营养",
              "product_second": "滋补养生",
              "product_third": "人参/西洋参"
            }
          }
        ]
      }
    }
  }
  ```

### 签名机制分析
- 每个请求包含 `timestamp`（毫秒级时间戳）和 `sign`（32位大写MD5）
- 签名计算方式需要从前端JS逆向获取（`app.b442a019c866446232c8.js`）
- **备选方案**：如果签名算法复杂，可直接使用固定参数模板（观察发现sign可能是固定值或简单计算）

## 实施方案

### 步骤1：创建Python爬虫脚本 `shark_shopping_spider.py`

**文件位置**：`/workspace/shark_shopping_spider.py`

**功能模块**：

1. **签名生成模块**
   - 分析前端JS中的sign生成逻辑
   - 实现对应的Python签名函数
   - 备选：如果签名验证不严格，尝试不带签名或使用固定签名

2. **API请求模块**
   - 封装3个API接口的请求函数
   - 使用 `requests` 库发送HTTP请求
   - 支持自定义日期查询

3. **数据解析模块**
   - 解析JSON响应数据
   - 将Unix时间戳转换为可读时间格式
   - 提取关键字段：播出时间、商品名称、价格、分类、品牌等

4. **数据输出模块**
   - 控制台表格化输出（使用 `tabulate` 或手动格式化）
   - 支持导出为CSV文件
   - 支持导出为JSON文件

5. **主程序入口**
   - 支持命令行参数指定日期范围
   - 默认获取当天节目表
   - 错误处理和日志输出

### 步骤2：测试验证
- 运行脚本获取当天节目数据
- 验证数据完整性和准确性
- 测试不同日期查询

## 关键代码设计

```python
# 核心数据结构
ProgramItem = {
    "日期": "2026-04-24",
    "开始时间": "00:00",
    "结束时间": "00:40",
    "分类": "滋补养生",
    "品牌": "其他",
    "商品名称": "御寿堂加拿大西洋参切片",
    "手机价": "369",
    "市场价": "399",
    "优惠信息": "立减30",
    "商品链接": "http://wp.sharkshopping.com/product/97094021",
    "商品图片": "http://..."
}
```

## 依赖库
- `requests` - HTTP请求
- `json` - JSON解析（标准库）
- `datetime` / `time` - 时间处理（标准库）
- `csv` - CSV导出（标准库）
- `hashlib` - MD5签名（标准库）
- `argparse` - 命令行参数（标准库）

## 假设与决策
1. **签名机制**：优先尝试逆向JS获取签名算法；如果签名验证宽松，使用简化方案
2. **城市编号**：默认使用 `310100`（上海），可通过参数修改
3. **输出格式**：默认控制台表格输出 + CSV文件导出
4. **Python版本**：兼容 Python 3.6+

## 验证步骤
1. 运行脚本获取当天节目数据，与网页展示对比验证
2. 测试历史日期查询功能
3. 验证CSV/JSON导出文件的完整性
4. 确认时间戳转换的准确性（注意时区，使用东八区）
