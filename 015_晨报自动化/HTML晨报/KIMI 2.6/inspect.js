const XLSX = require('xlsx');

const filePath = 'd:/project/HTML晨报/数据整理.xlsx';
const workbook = XLSX.readFile(filePath);

const sheet1 = workbook.Sheets[workbook.SheetNames[0]];
const data1 = XLSX.utils.sheet_to_json(sheet1, { header: 1 });

// 查看46165日期的所有渠道数据
console.log('=== 日期 46165 (2026/5/22) 的数据 ===');
const dayData = data1.slice(1).filter(r => r[0] === 46165);
dayData.forEach(r => {
  const channel = r[1];
  const order = r[2] || 0;
  const sales = r[3] || 0;
  const profit = r[4] || 0;
  console.log(`${channel}: 订购=${(order/10000).toFixed(1)}万, 销售=${(sales/10000).toFixed(1)}万, 利润=${(profit/10000).toFixed(1)}万`);
});

// 计算电视端及APP
const p1 = dayData.find(r => r[1] === 'P1');
const jt = dayData.find(r => r[1] === '金条还原');
const custom = dayData.find(r => r[1] === '定制类');
const private3 = dayData.find(r => r[1] === '私域第三方');

console.log('\n=== 计算汇总 ===');
console.log('P1:', p1 ? `订购=${(p1[2]/10000).toFixed(1)}, 销售=${(p1[3]/10000).toFixed(1)}, 利润=${(p1[4]/10000).toFixed(1)}` : '无');
console.log('金条还原:', jt ? `订购=${(jt[2]/10000).toFixed(1)}` : '无');
console.log('定制类:', custom ? `订购=${(custom[2]/10000).toFixed(1)}` : '无');
console.log('私域第三方:', private3 ? `订购=${(private3[2]/10000).toFixed(1)}, 利润=${(private3[4]/10000).toFixed(1)}` : '无');

const tvAppOrder = (p1?.[2]||0) + (jt?.[2]||0);
const tvAppSales = (p1?.[3]||0) + (jt?.[3]||0);
const tvAppProfit = (p1?.[4]||0) + (jt?.[4]||0);

console.log('\n电视端及APP:');
console.log(`  订购=${(tvAppOrder/10000).toFixed(1)}万`);
console.log(`  销售=${(tvAppSales/10000).toFixed(1)}万`);
console.log(`  利润=${(tvAppProfit/10000).toFixed(1)}万`);
console.log(`  转换率=${(tvAppSales/tvAppOrder*100).toFixed(1)}%`);
console.log(`  毛利率=${(tvAppProfit*1.13/tvAppSales*100).toFixed(1)}%`);

const totalGMV = tvAppOrder + (custom?.[2]||0) + (private3?.[2]||0);
const totalProfit = tvAppProfit + (private3?.[4]||0);
console.log(`\n全公司GMV=${(totalGMV/10000).toFixed(1)}万`);
console.log(`全公司销售利润=${(totalProfit/10000).toFixed(1)}万`);

// 对比参考图片：全公司GMV 574.0万，销售利润50.3万
console.log('\n=== 对比参考图片 ===');
console.log('参考: GMV=574.0万, 利润=50.3万');
console.log('实际:', `GMV=${(totalGMV/10000).toFixed(1)}万, 利润=${(totalProfit/10000).toFixed(1)}万`);
