/**
 * 数据处理器 - 处理Excel数据和计算逻辑
 */
class DataProcessor {
    constructor() {
        this.rawData = null;
        this.monthlyData = [];
        this.cumulativeData = [];
        this.targetData = [];
        this.maxDate = null;
    }

    /**
     * 加载并解析Excel文件
     */
    async loadExcel(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = new Uint8Array(e.target.result);
                    const workbook = XLSX.read(data, { type: 'array' });
                    this.parseWorkbook(workbook);
                    resolve(this);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = reject;
            reader.readAsArrayBuffer(file);
        });
    }

    /**
     * 解析工作簿
     */
    parseWorkbook(workbook) {
        // 解析月数据（每日更新）
        const monthlySheet = workbook.Sheets['月数据（每日更新）'];
        if (monthlySheet) {
            this.monthlyData = XLSX.utils.sheet_to_json(monthlySheet, { header: 1 });
            this.monthlyData = this.parseMonthlyData(this.monthlyData);
        }

        // 解析累计数据（每月更新）
        const cumulativeSheet = workbook.Sheets['累计数据（每月更新）'];
        if (cumulativeSheet) {
            this.cumulativeData = XLSX.utils.sheet_to_json(cumulativeSheet, { header: 1 });
            this.cumulativeData = this.parseCumulativeData(this.cumulativeData);
        }

        // 解析目标数据（每月更新）
        const targetSheet = workbook.Sheets['目标（每月更新）'];
        if (targetSheet) {
            this.targetData = XLSX.utils.sheet_to_json(targetSheet, { header: 1 });
            this.targetData = this.parseTargetData(this.targetData);
        }

        // 自动识别最大日期
        this.maxDate = this.findMaxDate();
    }

    /**
     * 解析月数据
     */
    parseMonthlyData(data) {
        if (data.length < 2) return [];
        
        const result = [];
        
        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            if (row.length < 3) continue;
            
            const item = {
                date: this.convertExcelDate(row[0]),
                channel: row[1],
                orderAmount: parseFloat(row[2]) || 0,
                salesAmount: parseFloat(row[3]) || 0,
                profit: parseFloat(row[4]) || 0
            };
            
            if (item.date) {
                result.push(item);
            }
        }
        
        return result;
    }

    /**
     * 解析累计数据
     */
    parseCumulativeData(data) {
        if (data.length < 2) return [];
        
        const result = [];
        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            if (row.length < 3) continue;
            
            result.push({
                channel: row[0],
                metric: row[1],
                value: parseFloat(row[2]) || 0
            });
        }
        
        return result;
    }

    /**
     * 解析目标数据
     */
    parseEuropeanNumber(value) {
        if (!value && value !== 0) return 0;
        const str = value.toString().trim();
        if (!str) return 0;
        const lastComma = str.lastIndexOf(',');
        const lastDot = str.lastIndexOf('.');
        if (lastComma > lastDot) {
            return parseFloat(str.replace(/\./g, '').replace(',', '.'));
        } else {
            return parseFloat(str.replace(/,/g, ''));
        }
    }

    parseTargetData(data) {
        if (data.length < 2) return [];
        
        const result = [];
        for (let i = 1; i < data.length; i++) {
            const row = data[i];
            if (row.length < 3) continue;
            
            result.push({
                month: parseInt(row[0]),
                orderTarget: this.parseEuropeanNumber(row[1]),
                salesTarget: this.parseEuropeanNumber(row[2]),
                profitTarget: this.parseEuropeanNumber(row[3]),
                channel: row[4],
                type: row[5]
            });
        }
        
        return result;
    }

    /**
     * 转换Excel日期
     */
    convertExcelDate(excelDate) {
        if (!excelDate) return null;
        if (typeof excelDate === 'number') {
            const epoch = new Date(Date.UTC(1899, 11, 30));
            const days = excelDate;
            const ms = days * 24 * 60 * 60 * 1000;
            const utcDate = new Date(epoch.getTime() + ms);
            return new Date(utcDate.getUTCFullYear(), utcDate.getUTCMonth(), utcDate.getUTCDate());
        }
        if (typeof excelDate === 'string') {
            return new Date(excelDate);
        }
        return null;
    }

    /**
     * 查找最大日期
     */
    findMaxDate() {
        if (!this.monthlyData || this.monthlyData.length === 0) return new Date();
        
        let maxDate = null;
        for (const item of this.monthlyData) {
            if (item.date && (!maxDate || item.date > maxDate)) {
                if (item.orderAmount > 0 || item.salesAmount > 0 || item.profit > 0) {
                    maxDate = item.date;
                }
            }
        }
        
        return maxDate || new Date();
    }

    /**
     * 获取可用日期列表
     */
    getAvailableDates() {
        const dates = [];
        const seen = new Set();
        
        for (const item of this.monthlyData) {
            if (item.date && !seen.has(item.date.getTime())) {
                if (item.orderAmount > 0 || item.salesAmount > 0 || item.profit > 0) {
                    dates.push(item.date);
                    seen.add(item.date.getTime());
                }
            }
        }
        
        return dates.sort((a, b) => b - a);
    }

    /**
     * 获取指定日期的数据
     */
    getDataByDate(date) {
        const targetDate = new Date(date);
        targetDate.setHours(0, 0, 0, 0);
        
        const dayData = this.monthlyData.filter(item => {
            if (!item.date) return false;
            const itemDate = new Date(item.date);
            itemDate.setHours(0, 0, 0, 0);
            return itemDate.getTime() === targetDate.getTime();
        });
        
        const year = targetDate.getFullYear();
        const month = targetDate.getMonth();
        const monthStart = new Date(year, month, 1);
        
        const monthData = this.monthlyData.filter(item => {
            if (!item.date) return false;
            const itemDate = new Date(item.date);
            itemDate.setHours(0, 0, 0, 0);
            return itemDate >= monthStart && itemDate <= targetDate;
        });
        
        const yearStart = new Date(year, 0, 1);
        const yearData = this.monthlyData.filter(item => {
            if (!item.date) return false;
            const itemDate = new Date(item.date);
            itemDate.setHours(0, 0, 0, 0);
            return itemDate >= yearStart && itemDate <= targetDate;
        });
        
        return {
            day: dayData,
            month: monthData,
            year: yearData,
            targetDate: targetDate
        };
    }

    /**
     * 计算表1数据 - 主要指标
     */
    calculateTable1(date) {
        const data = this.getDataByDate(date);
        const targetDate = data.targetDate;
        const year = targetDate.getFullYear();
        const month = targetDate.getMonth() + 1;
        const day = targetDate.getDate();
        
        const daysInMonth = new Date(year, month, 0).getDate();
        
        const channels = this.calculateChannelData(data, targetDate);
        const targets = this.calculateTargets(year, month, day, daysInMonth);
        
        return {
            date: targetDate,
            summary: this.calculateSummary(channels),
            channels: channels,
            targets: targets
        };
    }

    /**
     * 计算各渠道数据
     */
    getCumulativeValue(channel, metric, year) {
        const item = this.cumulativeData.find(c => 
            c.channel === channel && 
            c.metric === metric && 
            (c.year === undefined || c.year === year)
        );
        return item ? item.value : 0;
    }

    calculateChannelData(data, targetDate) {
        const channels = {};
        const year = targetDate ? targetDate.getFullYear() : new Date().getFullYear();
        
        const channelNames = ['P1', '金条还原', '定制类', '私域第三方', '白玉兰直播间', '自营供应链', '电视商品', '电商商品', '数据库营销', '私域东购部分'];
        channelNames.forEach(name => {
            channels[name] = {
                day: { order: 0, sales: 0, profit: 0 },
                month: { order: 0, sales: 0, profit: 0 },
                year: { order: 0, sales: 0, profit: 0 }
            };
        });
        
        data.day.forEach(item => {
            if (channels[item.channel]) {
                channels[item.channel].day.order += item.orderAmount;
                channels[item.channel].day.sales += item.salesAmount;
                channels[item.channel].day.profit += item.profit;
            }
        });
        
        data.month.forEach(item => {
            if (channels[item.channel]) {
                channels[item.channel].month.order += item.orderAmount;
                channels[item.channel].month.sales += item.salesAmount;
                channels[item.channel].month.profit += item.profit;
            }
        });
        
        data.year.forEach(item => {
            if (channels[item.channel]) {
                channels[item.channel].year.order += item.orderAmount;
                channels[item.channel].year.sales += item.salesAmount;
                channels[item.channel].year.profit += item.profit;
            }
        });
        
        // 加上累计数据sheet中之前月份的累计
        channelNames.forEach(name => {
            const cumOrder = this.getCumulativeValue(name, '订购额', year);
            const cumSales = this.getCumulativeValue(name, '销售额', year);
            const cumProfit = this.getCumulativeValue(name, '利润额', year);
            channels[name].year.order += cumOrder;
            channels[name].year.sales += cumSales;
            channels[name].year.profit += cumProfit;
        });
        
        // 电视端及APP = P1 + 金条还原
        channels['电视端及APP'] = {
            day: {
                order: channels['P1'].day.order + channels['金条还原'].day.order,
                sales: channels['P1'].day.sales + channels['金条还原'].day.sales,
                profit: channels['P1'].day.profit + channels['金条还原'].day.profit
            },
            month: {
                order: channels['P1'].month.order + channels['金条还原'].month.order,
                sales: channels['P1'].month.sales + channels['金条还原'].month.sales,
                profit: channels['P1'].month.profit + channels['金条还原'].month.profit
            },
            year: {
                order: channels['P1'].year.order + channels['金条还原'].year.order,
                sales: channels['P1'].year.sales + channels['金条还原'].year.sales,
                profit: channels['P1'].year.profit + channels['金条还原'].year.profit
            }
        };

        // 加上累计数据sheet中电视及APP的累计数据
        const tvAppCumOrder = this.getCumulativeValue('电视及APP', '订购额', year);
        const tvAppCumSales = this.getCumulativeValue('电视及APP', '销售额', year);
        const tvAppCumProfit = this.getCumulativeValue('电视及APP', '利润额', year);
        channels['电视端及APP'].year.order += tvAppCumOrder;
        channels['电视端及APP'].year.sales += tvAppCumSales;
        channels['电视端及APP'].year.profit += tvAppCumProfit;

        return channels;
    }

    /**
     * 计算汇总数据
     */
    calculateSummary(channels) {
        const gmv = {
            day: channels['电视端及APP'].day.order + channels['定制类'].day.order + channels['私域第三方'].day.order + channels['白玉兰直播间'].day.order,
            month: channels['电视端及APP'].month.order + channels['定制类'].month.order + channels['私域第三方'].month.order + channels['白玉兰直播间'].month.order,
            year: channels['电视端及APP'].year.order + channels['定制类'].year.order + channels['私域第三方'].year.order + channels['白玉兰直播间'].year.order
        };
        
        const profit = {
            day: channels['电视端及APP'].day.profit + channels['私域第三方'].day.profit,
            month: channels['电视端及APP'].month.profit + channels['私域第三方'].month.profit,
            year: channels['电视端及APP'].year.profit + channels['私域第三方'].year.profit
        };
        
        return { gmv, profit };
    }

    /**
     * 计算目标
     */
    calculateTargets(year, month, day, daysInMonth) {
        const targets = {
            电视及APP: { order: {}, sales: {}, profit: {} },
            自营供应链: { sales: {} },
            白玉兰直播间: { order: {} }
        };

        this.targetData.forEach(target => {
            // 电视及APP：当日和当月目标使用滚动目标，年累计目标使用年初目标
            if (target.channel === '电视及APP') {
                if (target.type === '滚动目标' && target.month === month) {
                    // 当日和当月目标使用滚动目标
                    targets.电视及APP.order.day = target.orderTarget / daysInMonth;
                    targets.电视及APP.order.month = target.orderTarget / daysInMonth * day;
                    targets.电视及APP.sales.day = target.salesTarget / daysInMonth;
                    targets.电视及APP.sales.month = target.salesTarget / daysInMonth * day;
                    targets.电视及APP.profit.day = target.profitTarget / daysInMonth;
                    targets.电视及APP.profit.month = target.profitTarget / daysInMonth * day;
                }
                if (target.type === '年初目标') {
                    // 年累计目标使用年初目标
                    if (target.month < month) {
                        targets.电视及APP.order.year = (targets.电视及APP.order.year || 0) + target.orderTarget;
                        targets.电视及APP.sales.year = (targets.电视及APP.sales.year || 0) + target.salesTarget;
                        targets.电视及APP.profit.year = (targets.电视及APP.profit.year || 0) + target.profitTarget;
                    } else if (target.month === month) {
                        targets.电视及APP.order.year = (targets.电视及APP.order.year || 0) + target.orderTarget / daysInMonth * day;
                        targets.电视及APP.sales.year = (targets.电视及APP.sales.year || 0) + target.salesTarget / daysInMonth * day;
                        targets.电视及APP.profit.year = (targets.电视及APP.profit.year || 0) + target.profitTarget / daysInMonth * day;
                    }
                }
            }

            if (target.channel === '自营供应链' && target.type === '年初目标') {
                if (target.month === month) {
                    targets.自营供应链.sales.day = target.salesTarget / daysInMonth;
                    targets.自营供应链.sales.month = target.salesTarget / daysInMonth * day;
                }
                if (target.month < month) {
                    targets.自营供应链.sales.year = (targets.自营供应链.sales.year || 0) + target.salesTarget;
                } else if (target.month === month) {
                    targets.自营供应链.sales.year = (targets.自营供应链.sales.year || 0) + target.salesTarget / daysInMonth * day;
                }
            }

            if (target.channel === '白玉兰直播间' && target.type === '年初目标') {
                if (target.month === month) {
                    targets.白玉兰直播间.order.day = target.orderTarget / daysInMonth;
                    targets.白玉兰直播间.order.month = target.orderTarget / daysInMonth * day;
                }
                if (target.month < month) {
                    targets.白玉兰直播间.order.year = (targets.白玉兰直播间.order.year || 0) + target.orderTarget;
                } else if (target.month === month) {
                    targets.白玉兰直播间.order.year = (targets.白玉兰直播间.order.year || 0) + target.orderTarget / daysInMonth * day;
                }
            }
        });

        return targets;
    }

    /**
     * 计算表2数据 - 业绩复盘
     */
    calculateTable2(date) {
        const data = this.getDataByDate(date);
        const targetDate = data.targetDate;
        const year = targetDate.getFullYear();
        const month = targetDate.getMonth() + 1;
        const day = targetDate.getDate();
        const daysInMonth = new Date(year, month, 0).getDate();
        
        const channels = this.calculateChannelData(data, targetDate);
        
        // 东方购物 = P1 + 私域第三方
        const dongfang = {
            profit: {
                day: channels['P1'].day.profit + channels['私域第三方'].day.profit,
                period: channels['P1'].month.profit + channels['私域第三方'].month.profit
            }
        };
        
        // 仅电视端及APP = P1 - 私域东购部分 - 数据库营销
        const tvOnly = {
            profit: {
                day: channels['P1'].day.profit - channels['私域东购部分'].day.profit - channels['数据库营销'].day.profit,
                period: channels['P1'].month.profit - channels['私域东购部分'].month.profit - channels['数据库营销'].month.profit
            }
        };
        
        // 私域 = 私域东购部分 + 私域第三方
        const privateDomain = {
            profit: {
                day: channels['私域东购部分'].day.profit + channels['私域第三方'].day.profit,
                period: channels['私域东购部分'].month.profit + channels['私域第三方'].month.profit
            }
        };
        
        const monthlyTargets = this.getMonthlyTargets(year, month);
        
        return {
            date: targetDate,
            daysInMonth: daysInMonth,
            day: day,
            profitSection: {
                东方购物: this.calculateProfitItem(dongfang.profit, monthlyTargets.东方购物, day, daysInMonth, ''),
                电视商品: this.calculateProfitItem({
                    day: channels['电视商品'].day.profit,
                    period: channels['电视商品'].month.profit
                }, monthlyTargets.电视商品, day, daysInMonth, '张凌云\n(温佳敏)'),
                电商商品: this.calculateProfitItem({
                    day: channels['电商商品'].day.profit,
                    period: channels['电商商品'].month.profit
                }, monthlyTargets.电商商品, day, daysInMonth, '张凌云'),
                仅电视端及APP: this.calculateProfitItem(tvOnly.profit, monthlyTargets.仅电视端及APP, day, daysInMonth, '曹俊\n(温佳敏)'),
                数据库营销: this.calculateProfitItem({
                    day: channels['数据库营销'].day.profit,
                    period: channels['数据库营销'].month.profit
                }, monthlyTargets.数据库营销, day, daysInMonth, '赵鹤/王涛'),
                私域: this.calculateProfitItem(privateDomain.profit, monthlyTargets.私域, day, daysInMonth, '张音祺')
            },
            salesSection: {
                自营供应链: this.calculateSalesItem({
                    day: channels['自营供应链'].day.sales,
                    period: channels['自营供应链'].month.sales
                }, monthlyTargets.自营供应链, day, daysInMonth, '许震威'),
                白玉兰直播间: this.calculateSalesItem({
                    day: channels['白玉兰直播间'].day.order,
                    period: channels['白玉兰直播间'].month.order
                }, monthlyTargets.白玉兰直播间, day, daysInMonth, '许震威')
            }
        };
    }

    /**
     * 获取月度目标
     */
    getMonthlyTargets(year, month) {
        const targets = {
            东方购物: 0,
            电视商品: 0,
            电商商品: 0,
            仅电视端及APP: 0,
            数据库营销: 0,
            私域: 0,
            自营供应链: 0,
            白玉兰直播间: 0
        };

        this.targetData.forEach(target => {
            if (target.month === month) {
                if (target.channel === '电视及APP' && target.type === '滚动目标') {
                    targets.东方购物 = target.profitTarget;
                }
                if (target.channel === '电视商品' && target.type === '滚动目标') {
                    targets.电视商品 = target.profitTarget;
                }
                if (target.channel === '电商商品' && target.type === '滚动目标') {
                    targets.电商商品 = target.profitTarget;
                }
                if (target.channel === '仅电视端及APP' && target.type === '滚动目标') {
                    targets.仅电视端及APP = target.profitTarget;
                }
                if (target.channel === '数据库营销' && target.type === '滚动目标') {
                    targets.数据库营销 = target.profitTarget;
                }
                if (target.channel === '私域' && target.type === '滚动目标') {
                    targets.私域 = target.profitTarget;
                }
                if (target.channel === '自营供应链' && target.type === '年初目标') {
                    targets.自营供应链 = target.salesTarget;
                }
                if (target.channel === '白玉兰直播间' && target.type === '年初目标') {
                    targets.白玉兰直播间 = target.orderTarget;
                }
            }
        });

        return targets;
    }

    /**
     * 计算利润项
     */
    calculateProfitItem(actual, monthlyTarget, day, daysInMonth, responsible = '') {
        const dailyTarget = monthlyTarget / daysInMonth;
        const periodTarget = dailyTarget * day;
        
        return {
            dailyTarget: dailyTarget,
            actualDay: actual.day,
            dayProgress: dailyTarget > 0 ? (actual.day / dailyTarget) : 0,
            periodTarget: periodTarget,
            actualPeriod: actual.period,
            deviation: actual.period - periodTarget,
            responsible: responsible
        };
    }

    /**
     * 计算销售项
     */
    calculateSalesItem(actual, monthlyTarget, day, daysInMonth, responsible) {
        const dailyTarget = monthlyTarget / daysInMonth;
        const periodTarget = dailyTarget * day;
        
        return {
            dailyTarget: dailyTarget,
            actualDay: actual.day,
            dayProgress: dailyTarget > 0 ? (actual.day / dailyTarget) : 0,
            periodTarget: periodTarget,
            actualPeriod: actual.period,
            deviation: actual.period - periodTarget,
            responsible: responsible
        };
    }

    /**
     * 格式化数字
     */
    static formatNumber(num, decimals = 1) {
        if (num === null || num === undefined || isNaN(num)) return '-';
        return num.toLocaleString('zh-CN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    /**
     * 格式化百分比
     */
    static formatPercent(num, decimals = 0) {
        if (num === null || num === undefined || isNaN(num)) return '-';
        return (num * 100).toFixed(decimals) + '%';
    }

    /**
     * 格式化日期
     */
    static formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        return `${d.getMonth() + 1}月${d.getDate()}日`;
    }

    /**
     * 格式化完整日期
     */
    static formatFullDate(date) {
        if (!date) return '';
        const d = new Date(date);
        const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
        return `${(d.getMonth() + 1).toString().padStart(2, '0')}月${d.getDate().toString().padStart(2, '0')}日（星期${weekdays[d.getDay()]}）`;
    }
}

// Node.js模块导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataProcessor;
}
