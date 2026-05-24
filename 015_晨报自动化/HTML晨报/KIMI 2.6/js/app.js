/**
 * 主应用逻辑
 */
class ReportApp {
    constructor() {
        this.dataProcessor = new DataProcessor();
        this.tableRenderer = new TableRenderer();
        this.currentDate = null;
        this.currentFile = null;
        
        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        this.bindEvents();
        this.checkSampleData();
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 文件上传
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });
        
        // 生成报表按钮
        document.getElementById('generateBtn').addEventListener('click', () => {
            this.generateReport();
        });
        
        // 使用示例数据按钮
        document.getElementById('useSampleBtn').addEventListener('click', () => {
            this.loadSampleData();
        });
        
        // 返回按钮
        document.getElementById('backBtn').addEventListener('click', () => {
            this.showUploadPage();
        });
        
        // 日期选择器
        document.getElementById('dateSelect').addEventListener('change', (e) => {
            if (e.target.value) {
                this.currentDate = new Date(e.target.value);
                this.updateReport();
            }
        });
        
        // 导出按钮
        document.getElementById('exportExcelBtn').addEventListener('click', () => {
            this.exportToExcel();
        });
        
        document.getElementById('exportJpgBtn').addEventListener('click', () => {
            this.exportToJpg();
        });

        document.getElementById('exportPdfBtn').addEventListener('click', () => {
            this.exportToPdf();
        });
    }

    /**
     * 检查示例数据
     */
    checkSampleData() {
        fetch('data/data.xlsx')
            .then(response => {
                if (!response.ok) {
                    document.getElementById('useSampleBtn').style.display = 'none';
                }
            })
            .catch(() => {
                document.getElementById('useSampleBtn').style.display = 'none';
            });
    }

    /**
     * 处理文件选择
     */
    handleFileSelect(file) {
        if (!file.name.endsWith('.xlsx')) {
            alert('请上传.xlsx格式的Excel文件');
            return;
        }
        
        this.currentFile = file;
        
        // 显示文件名
        const fileInfo = document.getElementById('fileInfo');
        fileInfo.querySelector('.file-name').textContent = file.name;
        fileInfo.style.display = 'flex';
    }

    /**
     * 加载示例数据
     */
    async loadSampleData() {
        this.showLoading(true);
        
        try {
            const response = await fetch('data/data.xlsx');
            if (!response.ok) {
                throw new Error('示例数据文件不存在');
            }
            
            const blob = await response.blob();
            const file = new File([blob], 'data.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            
            await this.dataProcessor.loadExcel(file);
            this.currentDate = this.dataProcessor.maxDate;
            this.showReportPage();
            this.populateDateSelect();
            this.updateReport();
        } catch (error) {
            console.error('加载示例数据失败:', error);
            alert('加载示例数据失败: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 生成报表
     */
    async generateReport() {
        if (!this.currentFile) {
            alert('请先选择Excel文件');
            return;
        }
        
        this.showLoading(true);
        
        try {
            await this.dataProcessor.loadExcel(this.currentFile);
            this.currentDate = this.dataProcessor.maxDate;
            this.showReportPage();
            this.populateDateSelect();
            this.updateReport();
        } catch (error) {
            console.error('生成报表失败:', error);
            alert('生成报表失败: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 填充日期选择器
     */
    populateDateSelect() {
        const dates = this.dataProcessor.getAvailableDates();
        this.tableRenderer.populateDateSelect(dates);
        
        // 设置当前选中的日期
        if (this.currentDate) {
            const d = new Date(this.currentDate);
            const yyyy = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, '0');
            const dd = String(d.getDate()).padStart(2, '0');
            document.getElementById('dateSelect').value = `${yyyy}-${mm}-${dd}`;
        }
    }

    /**
     * 更新报表
     */
    updateReport() {
        if (!this.currentDate) return;
        
        // 更新日期显示
        this.tableRenderer.updateDateDisplay(this.currentDate);
        
        // 计算并渲染表1
        const table1Data = this.dataProcessor.calculateTable1(this.currentDate);
        this.tableRenderer.renderTable1(table1Data);
        
        // 计算并渲染表2
        const table2Data = this.dataProcessor.calculateTable2(this.currentDate);
        this.tableRenderer.renderTable2(table2Data);
    }

    /**
     * 显示上传页面
     */
    showUploadPage() {
        document.getElementById('uploadPage').classList.add('active');
        document.getElementById('reportPage').classList.remove('active');
    }

    /**
     * 显示报表页面
     */
    showReportPage() {
        document.getElementById('uploadPage').classList.remove('active');
        document.getElementById('reportPage').classList.add('active');
    }

    /**
     * 显示/隐藏加载提示
     */
    showLoading(show) {
        document.getElementById('loading').style.display = show ? 'flex' : 'none';
    }

    /**
     * 导出为Excel
     */
    exportToExcel() {
        const table1 = document.querySelector('#table1Container table');
        const table2 = document.querySelector('#table2Container table');
        
        if (!table1 || !table2) {
            alert('没有可导出的数据');
            return;
        }
        
        // 创建工作簿
        const wb = XLSX.utils.book_new();
        
        // 导出表1
        const ws1 = XLSX.utils.table_to_sheet(table1);
        XLSX.utils.book_append_sheet(wb, ws1, '主要指标');
        
        // 导出表2
        const ws2 = XLSX.utils.table_to_sheet(table2);
        XLSX.utils.book_append_sheet(wb, ws2, '业绩复盘');
        
        // 保存文件
        const dateStr = this.formatDateForFile(this.currentDate);
        XLSX.writeFile(wb, `晨报_${dateStr}.xlsx`);
    }

    /**
     * 导出为JPG（300PPI）
     */
    async exportToJpg() {
        const reportContent = document.getElementById('reportContent');

        if (!reportContent.innerHTML.trim()) {
            alert('没有可导出的数据');
            return;
        }

        this.showLoading(true);

        try {
            // 获取报表内容的实际尺寸
            const rect = reportContent.getBoundingClientRect();
            const contentWidth = rect.width;
            const contentHeight = rect.height;

            // 300 PPI: 1 inch = 300 pixels
            // A4 width = 210mm ≈ 8.27 inch → 2480px at 300PPI
            const targetWidth = 2480;
            const scale = targetWidth / contentWidth;

            // 使用html2canvas将内容转换为图片，按300PPI比例缩放
            const canvas = await html2canvas(reportContent, {
                scale: scale,
                useCORS: true,
                allowTaint: true,
                backgroundColor: '#ffffff',
                width: contentWidth,
                height: contentHeight,
                windowWidth: contentWidth,
                windowHeight: contentHeight
            });

            // 转换为JPG并下载
            const imgData = canvas.toDataURL('image/jpeg', 0.95);
            const link = document.createElement('a');
            link.download = `晨报_${this.formatDateForFile(this.currentDate)}.jpg`;
            link.href = imgData;
            link.click();
        } catch (error) {
            console.error('导出JPG失败:', error);
            alert('导出JPG失败: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 导出为PDF
     */
    async exportToPdf() {
        const reportContent = document.getElementById('reportContent');
        
        if (!reportContent.innerHTML.trim()) {
            alert('没有可导出的数据');
            return;
        }
        
        this.showLoading(true);
        
        try {
            // 使用html2canvas将内容转换为图片
            const canvas = await html2canvas(reportContent, {
                scale: 2,
                useCORS: true,
                allowTaint: true,
                backgroundColor: '#ffffff'
            });
            
            // 创建PDF
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF('p', 'mm', 'a4');
            
            // 计算图片尺寸
            const imgWidth = 210;
            const pageHeight = 297;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
            
            let heightLeft = imgHeight;
            let position = 0;
            
            // 添加图片到PDF
            const imgData = canvas.toDataURL('image/png');
            
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
            
            // 如果内容超过一页，添加新页面
            while (heightLeft > 0) {
                position = heightLeft - imgHeight;
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                heightLeft -= pageHeight;
            }
            
            // 保存PDF
            const dateStr = this.formatDateForFile(this.currentDate);
            pdf.save(`晨报_${dateStr}.pdf`);
        } catch (error) {
            console.error('导出PDF失败:', error);
            alert('导出PDF失败: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * 格式化日期用于文件名
     */
    formatDateForFile(date) {
        if (!date) return '';
        const d = new Date(date);
        const yyyy = d.getFullYear();
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        return `${yyyy}${mm}${dd}`;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ReportApp();
});
