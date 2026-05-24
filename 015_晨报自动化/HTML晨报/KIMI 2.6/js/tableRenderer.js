/**
 * 表格渲染器 - 渲染表1和表2
 */
class TableRenderer {
    constructor() {
        this.formatter = DataProcessor;
    }

    /**
     * 渲染表1 - 主要指标
     */
    renderTable1(data) {
        const container = document.getElementById('table1Container');
        const summary = document.getElementById('gmvSummary');
        const title = document.getElementById('table1Title');
        
        // 更新标题和汇总
        const dateStr = this.formatter.formatFullDate(data.date);
        title.textContent = `${dateStr} 主要指标`;
        summary.innerHTML = `
            <span>全公司GMV ${this.formatWan(data.summary.gmv.day)}万（含定制类${this.formatWan(data.channels['定制类'].day.order)}万）；销售利润 ${this.formatWan(data.summary.profit.day)}万；</span>
            <span style="margin-left: 20px;">单位：万元</span>
        `;
        
        // 构建表格HTML
        let html = '<table class="data-table">';
        
        // 表头
        html += `
            <thead class="red-header">
                <tr>
                    <th colspan="2">东方购物</th>
                    <th colspan="3">当日</th>
                    <th colspan="3">月累计</th>
                    <th colspan="3">年累计</th>
                </tr>
                <tr>
                    <th>渠道</th>
                    <th>指标</th>
                    <th>数值</th>
                    <th>达成率</th>
                    <th>目标偏差</th>
                    <th>数值</th>
                    <th>达成率</th>
                    <th>目标偏差</th>
                    <th>数值</th>
                    <th>达成率</th>
                    <th>目标偏差</th>
                </tr>
            </thead>
        `;
        
        // 表体
        html += '<tbody>';
        
        // 东方购物 - 电视端及APP
        const tvApp = data.channels['电视端及APP'];
        const tvAppTarget = data.targets.电视及APP;
        const tvAppRowspan = 5;
        
        // 第一行：渠道名 + 转换率
        const conversionRate = {
            day: tvApp.day.order > 0 ? tvApp.day.sales / tvApp.day.order : 0,
            month: tvApp.month.order > 0 ? tvApp.month.sales / tvApp.month.order : 0,
            year: tvApp.year.order > 0 ? tvApp.year.sales / tvApp.year.order : 0
        };
        html += `<tr>
            <td rowspan="${tvAppRowspan}">电视端及APP（P1+金条还原）</td>
            <td>转换率</td>
            <td class="percentage">${this.formatter.formatPercent(conversionRate.day, 1)}</td>
            <td>-</td><td>-</td>
            <td class="percentage">${this.formatter.formatPercent(conversionRate.month, 1)}</td>
            <td>-</td><td>-</td>
            <td class="percentage">${this.formatter.formatPercent(conversionRate.year, 1)}</td>
            <td>-</td><td>-</td>
        </tr>`;
        
        // 第二行：毛利率
        const grossMargin = {
            day: tvApp.day.sales > 0 ? tvApp.day.profit * 1.13 / tvApp.day.sales : 0,
            month: tvApp.month.sales > 0 ? tvApp.month.profit * 1.13 / tvApp.month.sales : 0,
            year: tvApp.year.sales > 0 ? tvApp.year.profit * 1.13 / tvApp.year.sales : 0
        };
        html += this.renderMetricRow('毛利率', grossMargin, '%', null, true);
        
        // 第三行：订购额
        html += this.renderMetricRow('订购额', {
            day: tvApp.day.order,
            month: tvApp.month.order,
            year: tvApp.year.order
        }, '万', tvAppTarget.order);
        
        // 第四行：销售额
        html += this.renderMetricRow('销售额', {
            day: tvApp.day.sales,
            month: tvApp.month.sales,
            year: tvApp.year.sales
        }, '万', tvAppTarget.sales);
        
        // 第五行：销售利润
        html += this.renderMetricRow('销售利润', {
            day: tvApp.day.profit,
            month: tvApp.month.profit,
            year: tvApp.year.profit
        }, '万', tvAppTarget.profit);
        
        html += '</tbody>';
        
        // 定制类（黄色表头）
        const dingzhi = data.channels['定制类'];
        html += `
            <thead class="yellow-header">
                <tr>
                    <th colspan="2">定制类</th>
                    <th colspan="3">当日</th>
                    <th colspan="3">月累计</th>
                    <th colspan="3">年累计</th>
                </tr>
            </thead>
            <tbody>
        `;
        html += this.renderSimpleRow('订购额', {
            day: dingzhi.day.order,
            month: dingzhi.month.order,
            year: dingzhi.year.order
        });
        html += '</tbody>';
        
        // 私域第三方（黄色表头）
        const siyu = data.channels['私域第三方'];
        html += `
            <thead class="yellow-header">
                <tr>
                    <th colspan="2">私域第三方</th>
                    <th colspan="3">当日</th>
                    <th colspan="3">月累计</th>
                    <th colspan="3">年累计</th>
                </tr>
            </thead>
            <tbody>
        `;
        html += this.renderSimpleRow('订购额', {
            day: siyu.day.order,
            month: siyu.month.order,
            year: siyu.year.order
        });
        html += '</tbody>';
        
        // 自营供应链（深蓝色表头）
        const ziying = data.channels['自营供应链'];
        const ziyingTarget = data.targets.自营供应链;
        html += `
            <thead class="blue-header">
                <tr>
                    <th colspan="2">自营供应链</th>
                    <th colspan="3">当日</th>
                    <th colspan="3">月累计</th>
                    <th colspan="3">年累计</th>
                </tr>
            </thead>
            <tbody>
        `;
        html += `<tr>
            <td></td>
            <td>销售额</td>
            <td class="number">${this.formatWan(ziying.day.sales)}</td>
            <td class="achievement-rate ${this.getAchievementClass(ziyingTarget.sales.day > 0 ? ziying.day.sales / ziyingTarget.sales.day : 0)}">${this.formatter.formatPercent(ziyingTarget.sales.day > 0 ? ziying.day.sales / ziyingTarget.sales.day : 0, 0)}</td>
            <td class="deviation ${ziying.day.sales - ziyingTarget.sales.day >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(ziying.day.sales - ziyingTarget.sales.day)}</td>
            <td class="number">${this.formatWan(ziying.month.sales)}</td>
            <td class="achievement-rate ${this.getAchievementClass(ziyingTarget.sales.month > 0 ? ziying.month.sales / ziyingTarget.sales.month : 0)}">${this.formatter.formatPercent(ziyingTarget.sales.month > 0 ? ziying.month.sales / ziyingTarget.sales.month : 0, 0)}</td>
            <td class="deviation ${ziying.month.sales - ziyingTarget.sales.month >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(ziying.month.sales - ziyingTarget.sales.month)}</td>
            <td class="number">${this.formatWan(ziying.year.sales)}</td>
            <td class="achievement-rate ${this.getAchievementClass(ziyingTarget.sales.year > 0 ? ziying.year.sales / ziyingTarget.sales.year : 0)}">${this.formatter.formatPercent(ziyingTarget.sales.year > 0 ? ziying.year.sales / ziyingTarget.sales.year : 0, 0)}</td>
            <td class="deviation ${ziying.year.sales - ziyingTarget.sales.year >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(ziying.year.sales - ziyingTarget.sales.year)}</td>
        </tr>`;
        html += '</tbody>';

        // 白玉兰直播间（深蓝色表头）
        const baiyu = data.channels['白玉兰直播间'];
        const baiyuTarget = data.targets.白玉兰直播间;
        html += `
            <thead class="blue-header">
                <tr>
                    <th colspan="2">白玉兰直播间</th>
                    <th colspan="3">当日</th>
                    <th colspan="3">月累计</th>
                    <th colspan="3">年累计</th>
                </tr>
            </thead>
            <tbody>
        `;
        html += `<tr>
            <td></td>
            <td>GMV</td>
            <td class="number">${this.formatWan(baiyu.day.order)}</td>
            <td class="achievement-rate ${this.getAchievementClass(baiyuTarget.order.day > 0 ? baiyu.day.order / baiyuTarget.order.day : 0)}">${this.formatter.formatPercent(baiyuTarget.order.day > 0 ? baiyu.day.order / baiyuTarget.order.day : 0, 0)}</td>
            <td class="deviation ${baiyu.day.order - baiyuTarget.order.day >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(baiyu.day.order - baiyuTarget.order.day)}</td>
            <td class="number">${this.formatWan(baiyu.month.order)}</td>
            <td class="achievement-rate ${this.getAchievementClass(baiyuTarget.order.month > 0 ? baiyu.month.order / baiyuTarget.order.month : 0)}">${this.formatter.formatPercent(baiyuTarget.order.month > 0 ? baiyu.month.order / baiyuTarget.order.month : 0, 0)}</td>
            <td class="deviation ${baiyu.month.order - baiyuTarget.order.month >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(baiyu.month.order - baiyuTarget.order.month)}</td>
            <td class="number">${this.formatWan(baiyu.year.order)}</td>
            <td class="achievement-rate ${this.getAchievementClass(baiyuTarget.order.year > 0 ? baiyu.year.order / baiyuTarget.order.year : 0)}">${this.formatter.formatPercent(baiyuTarget.order.year > 0 ? baiyu.year.order / baiyuTarget.order.year : 0, 0)}</td>
            <td class="deviation ${baiyu.year.order - baiyuTarget.order.year >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(baiyu.year.order - baiyuTarget.order.year)}</td>
        </tr>`;
        html += '</tbody>';
        
        html += '</table>';
        container.innerHTML = html;

        // 更新备注第4条：动态计算日均目标
        const dongfangDailyTarget = this.formatWan(data.targets.电视及APP.order.day);
        const baiyuDailyTarget = this.formatWan(data.targets.白玉兰直播间.order.day);
        const note4 = document.querySelector('.notes-section ol li:nth-child(4)');
        if (note4) {
            const year = data.date.getFullYear();
            const month = data.date.getMonth() + 1;
            note4.textContent = `${year}年${month}月，东方购物日均订购目标 ${dongfangDailyTarget}万、白玉兰直播间日均GMV目标${baiyuDailyTarget}万。`;
        }
    }

    /**
     * 渲染渠道行
     */
    renderChannelRow(channelName, subName, data, target, showMetrics) {
        let html = '<tr>';
        html += `<td rowspan="${showMetrics ? 6 : 1}">${channelName}${subName ? '<br><small>' + subName + '</small>' : ''}</td>`;
        html += `<td>${showMetrics ? '转换率' : '订购额'}</td>`;
        
        if (showMetrics) {
            const rate = data.day.sales / data.day.order;
            html += `<td class="percentage">${this.formatter.formatPercent(rate, 1)}</td>`;
            html += `<td>-</td><td>-</td>`;
            
            const monthRate = data.month.sales / data.month.order;
            html += `<td class="percentage">${this.formatter.formatPercent(monthRate, 1)}</td>`;
            html += `<td>-</td><td>-</td>`;
            
            const yearRate = data.year.sales / data.year.order;
            html += `<td class="percentage">${this.formatter.formatPercent(yearRate, 1)}</td>`;
            html += `<td>-</td><td>-</td>`;
        } else {
            const value = data.day.order;
            html += `<td class="number">${this.formatWan(value)}</td>`;
            html += `<td>-</td><td>-</td>`;
            html += `<td class="number">${this.formatWan(data.month.order)}</td>`;
            html += `<td>-</td><td>-</td>`;
            html += `<td class="number">${this.formatWan(data.year.order)}</td>`;
            html += `<td>-</td><td>-</td>`;
        }
        
        html += '</tr>';
        return html;
    }

    /**
     * 渲染指标行
     */
    renderMetricRow(metricName, values, unit, target = null, noBold = false) {
        let html = '<tr>';
        html += `<td${noBold ? ' style="font-weight:normal"' : ''}>${metricName}</td>`;
        
        // 当日
        if (unit === '%') {
            html += `<td class="percentage">${this.formatter.formatPercent(values.day, 1)}</td>`;
            html += `<td>-</td><td>-</td>`;
        } else {
            html += `<td class="number">${this.formatWan(values.day)}</td>`;
            if (target) {
                const achievement = target.day > 0 ? values.day / target.day : 0;
                const deviation = values.day - target.day;
                html += `<td class="achievement-rate ${this.getAchievementClass(achievement)}">${this.formatter.formatPercent(achievement, 0)}</td>`;
                html += `<td class="deviation ${deviation >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(deviation)}</td>`;
            } else {
                html += `<td>-</td><td>-</td>`;
            }
        }
        
        // 月累计
        if (unit === '%') {
            html += `<td class="percentage">${this.formatter.formatPercent(values.month, 1)}</td>`;
            html += `<td>-</td><td>-</td>`;
        } else {
            html += `<td class="number">${this.formatWan(values.month)}</td>`;
            if (target) {
                const monthAchievement = target.month > 0 ? values.month / target.month : 0;
                const monthDeviation = values.month - target.month;
                html += `<td class="achievement-rate ${this.getAchievementClass(monthAchievement)}">${this.formatter.formatPercent(monthAchievement, 0)}</td>`;
                html += `<td class="deviation ${monthDeviation >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(monthDeviation)}</td>`;
            } else {
                html += `<td>-</td><td>-</td>`;
            }
        }
        
        // 年累计
        if (unit === '%') {
            html += `<td class="percentage">${this.formatter.formatPercent(values.year, 1)}</td>`;
            html += `<td>-</td><td>-</td>`;
        } else {
            html += `<td class="number">${this.formatWan(values.year)}</td>`;
            if (target) {
                const yearAchievement = target.year > 0 ? values.year / target.year : 0;
                const yearDeviation = values.year - target.year;
                html += `<td class="achievement-rate ${this.getAchievementClass(yearAchievement)}">${this.formatter.formatPercent(yearAchievement, 0)}</td>`;
                html += `<td class="deviation ${yearDeviation >= 0 ? 'positive' : 'negative'}">${this.formatDeviation(yearDeviation)}</td>`;
            } else {
                html += `<td>-</td><td>-</td>`;
            }
        }
        
        html += '</tr>';
        return html;
    }

    /**
     * 渲染简单行（无目标）
     */
    renderSimpleRow(metricName, values) {
        let html = '<tr>';
        html += `<td></td><td>${metricName}</td>`;
        html += `<td class="number">${this.formatWan(values.day)}</td>`;
        html += `<td>-</td><td>-</td>`;
        html += `<td class="number">${this.formatWan(values.month)}</td>`;
        html += `<td>-</td><td>-</td>`;
        html += `<td class="number">${this.formatWan(values.year)}</td>`;
        html += `<td>-</td><td>-</td>`;
        html += '</tr>';
        return html;
    }

    /**
     * 渲染表2 - 业绩复盘
     */
    renderTable2(data) {
        const container = document.getElementById('table2Container');
        const title = document.getElementById('table2Title');
        
        const dateStr = this.formatter.formatFullDate(data.date);
        title.textContent = `${dateStr} 业绩复盘`;
        
        let html = '<table class="data-table table2">';
        
        // 第一部分：销售利润
        html += `
            <thead class="red-header">
                <tr>
                    <th>销售利润</th>
                    <th>月度<br>日均标</th>
                    <th>当日<br>利润</th>
                    <th>当日<br>进度</th>
                    <th>期间<br>利润</th>
                    <th>期间<br>偏差</th>
                    <th>责任人</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        // 东方购物行
        const dongfang = data.profitSection.东方购物;
        html += this.renderTable2Row('东方购物', dongfang, dongfang.responsible, false, true);
        
        // 电视商品行
        const dianshi = data.profitSection.电视商品;
        html += this.renderTable2Row('电视商品', dianshi, dianshi.responsible, true, false);
        
        // 电商商品行
        const dianshang = data.profitSection.电商商品;
        html += this.renderTable2Row('电商商品', dianshang, dianshang.responsible, true, false);
        
        // 仅电视端及APP行
        const tvOnly = data.profitSection.仅电视端及APP;
        html += this.renderTable2Row('仅电视端及APP', tvOnly, tvOnly.responsible, false, false, true);
        
        // 数据库营销行
        const db = data.profitSection.数据库营销;
        html += this.renderTable2Row('数据库营销', db, db.responsible, true, false);
        
        // 私域行
        const siyu = data.profitSection.私域;
        html += this.renderTable2Row('私域', siyu, siyu.responsible, false, false, true);
        
        html += '</tbody>';
        
        // 第二部分：销售/GMV
        html += `
            <thead class="red-header">
                <tr>
                    <th>销售/GMV</th>
                    <th>月度<br>日均标</th>
                    <th>业绩</th>
                    <th>当日<br>进度</th>
                    <th>期间<br>业绩</th>
                    <th>期间<br>偏差</th>
                    <th>责任人</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        // 自营供应链行
        const ziying = data.salesSection.自营供应链;
        html += this.renderTable2Row('自营供应链<br>销售额', ziying, ziying.responsible, false, true);
        
        // 白玉兰直播间行
        const baiyu = data.salesSection.白玉兰直播间;
        html += this.renderTable2Row('白玉兰直播间<br>GMV', baiyu, baiyu.responsible, false, true);
        
        html += '</tbody></table>';
        container.innerHTML = html;
    }

    /**
     * 渲染表2行
     */
    renderTable2Row(name, data, responsible, indent, highlight, noBold = false) {
        let html = `<tr class="${highlight ? 'highlight-row' : ''} ${indent ? 'indent' : ''} ${noBold ? 'no-bold' : ''}">`;
        
        html += `<td>${name}</td>`;
        
        // 月度日均标
        html += `<td class="number">${this.formatWan(data.dailyTarget)}</td>`;
        
        // 当日利润/业绩
        html += `<td class="number value-red">${this.formatWan(data.actualDay)}</td>`;
        
        // 当日进度
        if (data.dailyTarget > 0) {
            const progressClass = data.dayProgress >= 1 ? 'high' : (data.dayProgress >= 0.8 ? 'medium' : 'low');
            html += `<td class="achievement-rate progress-${progressClass}">${this.formatter.formatPercent(data.dayProgress, 0)}</td>`;
        } else {
            html += `<td>-</td>`;
        }
        
        // 期间利润/业绩
        html += `<td class="number value-red">${this.formatWan(data.actualPeriod)}</td>`;
        
        // 期间偏差
        const deviationClass = data.deviation >= 0 ? 'positive' : 'negative';
        html += `<td class="deviation ${deviationClass}">${this.formatDeviation(data.deviation)}</td>`;
        
        // 责任人 - 支持换行显示
        const responsibleDisplay = responsible ? responsible.replace(/\\n/g, '<br>') : '-';
        html += `<td>${responsibleDisplay}</td>`;
        
        html += '</tr>';
        return html;
    }

    /**
     * 格式化万元
     */
    formatWan(value) {
        if (value === null || value === undefined || isNaN(value)) return '-';
        return (value / 10000).toFixed(1);
    }

    /**
     * 格式化偏差
     */
    formatDeviation(value) {
        if (value === null || value === undefined || isNaN(value)) return '-';
        const arrow = value >= 0 ? '↑' : '↓';
        return `${arrow} ${Math.abs(value / 10000).toFixed(1)}`;
    }

    /**
     * 获取达成率样式类
     */
    getAchievementClass(rate) {
        if (rate >= 1) return 'high';
        if (rate >= 0.8) return 'medium';
        return 'low';
    }

    /**
     * 更新日期显示
     */
    updateDateDisplay(date) {
        const dateInfo = document.getElementById('dateInfo');
        const dateSelect = document.getElementById('dateSelect');
        
        const formatted = this.formatter.formatFullDate(date);
        dateInfo.textContent = formatted;
        
        // 设置日期选择器的值
        const d = new Date(date);
        const yyyy = d.getFullYear();
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        dateSelect.value = `${yyyy}-${mm}-${dd}`;
    }

    /**
     * 填充日期选择器
     */
    populateDateSelect(dates) {
        const select = document.getElementById('dateSelect');
        select.innerHTML = '<option value="">请选择日期</option>';
        
        dates.forEach(date => {
            const d = new Date(date);
            const yyyy = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, '0');
            const dd = String(d.getDate()).padStart(2, '0');
            const value = `${yyyy}-${mm}-${dd}`;
            const text = this.formatter.formatFullDate(date);
            
            const option = document.createElement('option');
            option.value = value;
            option.textContent = text;
            select.appendChild(option);
        });
    }
}
