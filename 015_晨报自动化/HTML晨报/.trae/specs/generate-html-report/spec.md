# HTML晨报生成器 - 产品需求文档

## Overview
- **Summary**: 根据Excel数据自动生成两张HTML表格（主要指标表和业绩复盘表），参考样式图片的设计风格
- **Purpose**: 自动生成日报/周报的HTML报表，便于数据展示和分享
- **Target Users**: 数据分析人员、业务人员

## Goals
- 从Excel文件读取数据并解析
- 生成符合参考样式的主要指标表（表1）
- 生成符合参考样式的业绩复盘表（表2）
- 支持数据自动计算（达成率、目标偏差等）

## Non-Goals (Out of Scope)
- 不支持实时数据更新
- 不支持交互式图表功能
- 不支持数据导出功能

## Background & Context
- 数据源：`数据整理.xlsx`包含三个sheet（月数据、累计数据、目标数据）
- 样式参考：`数据样式.xlsm`和`表1.png`、`表2.png`
- 输出目录：`trea/`下生成HTML应用

## Functional Requirements
- **FR-1**: 读取Excel文件中的月数据（每日更新）sheet
- **FR-2**: 读取Excel文件中的累计数据（每月更新）sheet
- **FR-3**: 读取Excel文件中的目标（每月更新）sheet
- **FR-4**: 根据参考样式生成主要指标表格（表1）
- **FR-5**: 根据参考样式生成业绩复盘表格（表2）
- **FR-6**: 计算达成率和目标偏差等衍生指标

## Non-Functional Requirements
- **NFR-1**: HTML页面需保持良好的视觉样式，与参考图片风格一致
- **NFR-2**: 数据计算需准确，支持四舍五入显示
- **NFR-3**: 页面需在主流浏览器中正常显示

## Constraints
- **Technical**: 使用纯HTML/CSS/JavaScript实现，无需后端
- **Business**: 数据来源于指定Excel文件，格式固定

## Assumptions
- Excel文件格式保持不变
- 日期格式为Excel日期序列号（需转换为实际日期）
- 数据单位为万元（需根据实际数值调整显示）

## Acceptance Criteria

### AC-1: 主要指标表生成
- **Given**: Excel数据已读取
- **When**: 页面加载
- **Then**: 显示包含东方购物、定制类、私域第三方、自营供应链、白玉兰直播间的主要指标表格
- **Verification**: `human-judgment`

### AC-2: 业绩复盘表生成
- **Given**: Excel数据已读取
- **When**: 页面加载
- **Then**: 显示包含销售利润和销售/GMV的业绩复盘表格
- **Verification**: `human-judgment`

### AC-3: 数据准确性
- **Given**: Excel数据包含正确的数值
- **When**: 页面加载
- **Then**: 表格中的数值与Excel数据一致，计算的达成率和偏差正确
- **Verification**: `programmatic`

### AC-4: 样式匹配
- **Given**: 参考图片包含特定颜色和布局
- **When**: 页面加载
- **Then**: HTML表格样式与参考图片一致
- **Verification**: `human-judgment`

## Open Questions
- [ ] 日期显示格式（当前数据为Excel序列号，需确定显示格式）
- [ ] 数值单位转换（Excel中的数值可能需要转换为万元显示）