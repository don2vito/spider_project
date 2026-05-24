const XLSX = require('xlsx');

// 模拟浏览器环境
global.XLSX = XLSX;

// 加载DataProcessor
const DataProcessor = require('./js/dataProcessor.js');

async function test() {
    const dp = new DataProcessor();
    
    // 读取Excel
    const workbook = XLSX.readFile('d:/project/HTML晨报/数据整理.xlsx');
    dp.parseWorkbook(workbook);
    
    console.log('=== 测试数据处理器 ===');
    
    // 获取最新日期
    const maxDate = dp.maxDate;
    console.log('最新日期:', maxDate.toLocaleDateString('zh-CN'));
    
    // 获取可用日期
    const dates = dp.getAvailableDates();
    console.log('可用日期数:', dates.length);
    
    // 测试表1数据
    console.log('\n=== 表1数据 ===');
    const table1Data = dp.calculateTable1(maxDate);
    console.log('日期:', DataProcessor.formatFullDate(table1Data.date));
    console.log('全公司GMV:', (table1Data.summary.gmv.day / 10000).toFixed(1), '万');
    console.log('全公司销售利润:', (table1Data.summary.profit.day / 10000).toFixed(1), '万');
    
    console.log('\n电视端及APP:');
    const tvApp = table1Data.channels['电视端及APP'];
    console.log('  订购额-当日:', (tvApp.day.order / 10000).toFixed(1), '万');
    console.log('  销售额-当日:', (tvApp.day.sales / 10000).toFixed(1), '万');
    console.log('  利润-当日:', (tvApp.day.profit / 10000).toFixed(1), '万');
    console.log('  转换率:', (tvApp.day.sales / tvApp.day.order * 100).toFixed(1) + '%');
    console.log('  毛利率:', (tvApp.day.profit * 1.13 / tvApp.day.sales * 100).toFixed(1) + '%');
    
    console.log('\n目标:');
    console.log('  电视及APP订购目标-当日:', (table1Data.targets.电视及APP.order.day / 10000).toFixed(1), '万');
    console.log('  电视及APP销售目标-当日:', (table1Data.targets.电视及APP.sales.day / 10000).toFixed(1), '万');
    console.log('  电视及APP利润目标-当日:', (table1Data.targets.电视及APP.profit.day / 10000).toFixed(1), '万');
    
    // 测试表2数据
    console.log('\n=== 表2数据 ===');
    const table2Data = dp.calculateTable2(maxDate);
    console.log('日期:', DataProcessor.formatFullDate(table2Data.date));
    
    console.log('\n销售利润:');
    Object.keys(table2Data.profitSection).forEach(key => {
        const row = table2Data.profitSection[key];
        console.log(`  ${key}:`);
        console.log(`    月度日均标: ${(row.dailyTarget / 10000).toFixed(1)}万`);
        console.log(`    当日利润: ${(row.actualDay / 10000).toFixed(1)}万`);
        console.log(`    当日进度: ${(row.dayProgress * 100).toFixed(0)}%`);
        console.log(`    期间利润: ${(row.actualPeriod / 10000).toFixed(1)}万`);
        console.log(`    期间偏差: ${(row.deviation / 10000).toFixed(1)}万`);
    });
    
    console.log('\n销售/GMV:');
    Object.keys(table2Data.salesSection).forEach(key => {
        const row = table2Data.salesSection[key];
        console.log(`  ${key}:`);
        console.log(`    月度日均标: ${(row.dailyTarget / 10000).toFixed(1)}万`);
        console.log(`    当日业绩: ${(row.actualDay / 10000).toFixed(1)}万`);
        console.log(`    当日进度: ${(row.dayProgress * 100).toFixed(0)}%`);
        console.log(`    期间业绩: ${(row.actualPeriod / 10000).toFixed(1)}万`);
        console.log(`    期间偏差: ${(row.deviation / 10000).toFixed(1)}万`);
        console.log(`    责任人: ${row.responsible}`);
    });
}

test().catch(console.error);
