/**
 * CBNData 报告中心 - 前端交互逻辑
 */

const API_BASE = '';  // 同源部署，留空

// ── 工具函数 ───────────────────────────────────────────────

function proxyImageUrl(originalUrl) {
    // 通过服务端代理加载图片，解决跨域和 Referer 问题
    if (!originalUrl) return '';
    return `${API_BASE}/api/proxy-image?url=${encodeURIComponent(originalUrl)}`;
}

// ── DOM 元素引用 ────────────────────────────────────────────
const $loading = document.getElementById('loading');
const $loadingSubtext = document.getElementById('loadingSubtext');
const $errorPanel = document.getElementById('errorPanel');
const $errorMessage = document.getElementById('errorMessage');
const $statsBar = document.getElementById('statsBar');
const $tableWrapper = document.getElementById('tableWrapper');
const $reportTableBody = document.getElementById('reportTableBody');
const $totalCount = document.getElementById('totalCount');
const $totalPages = document.getElementById('totalPages');
const $dateRange = document.getElementById('dateRange');
const $downloadModal = document.getElementById('downloadModal');
const $modalTitle = document.getElementById('modalTitle');
const $modalCloseBtn = document.getElementById('modalCloseBtn');
const $progressFill = document.getElementById('progressFill');
const $progressText = document.getElementById('progressText');
const $progressPercent = document.getElementById('progressPercent');
const $modalDetail = document.getElementById('modalDetail');

// ── 状态 ───────────────────────────────────────────────────
let reportsCache = [];
let isDownloading = false;

// ── 页面初始化 ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    fetchReports();
});

// ── 数据获取 ───────────────────────────────────────────────

async function fetchReports(forceRefresh = false) {
    showLoading();
    hideError();
    hideTable();
    hideStats();

    const params = new URLSearchParams();
    if (forceRefresh) params.set('refresh', '1');

    try {
        $loadingSubtext.textContent = '正在连接 CBNData 数据源...';

        const resp = await fetch(`${API_BASE}/api/reports?${params.toString()}`);

        if (!resp.ok) {
            throw new Error(`服务器返回错误 (${resp.status})`);
        }

        $loadingSubtext.textContent = '正在解析报告数据...';

        const result = await resp.json();

        if (!result.success) {
            throw new Error(result.error || '获取数据失败');
        }

        if (!result.data || result.data.length === 0) {
            $loadingSubtext.textContent = '当前年度暂无免费报告';
            setTimeout(() => {
                hideLoading();
                showError('当前年度暂无免费报告数据');
            }, 1500);
            return;
        }

        reportsCache = result.data;
        renderReports(result.data);
        updateStats(result.data);
        showStats();
        showTable();

        // 更新年份标签
        document.getElementById('yearLabel').textContent =
            `${result.year} 年度免费报告 · 第一财经商业数据中心`;

    } catch (err) {
        console.error('获取报告失败:', err);
        showError(err.message);
    } finally {
        hideLoading();
    }
}

// ── 渲染报告表格 ───────────────────────────────────────────

function renderReports(reports) {
    // 按日期升序排列（API 返回倒序，需反转）
    const sorted = [...reports].sort((a, b) =>
        new Date(a.date) - new Date(b.date)
    );

    $reportTableBody.innerHTML = sorted.map((r, index) => `
        <tr style="animation: fadeSlideUp 0.3s ease-out ${index * 0.02}s both">
            <td class="col-cover">
                <img
                    src="${proxyImageUrl(r.thumbnail_url)}"
                    alt="${escapeHtml(r.title)}"
                    loading="lazy"
                    onerror="this.src='data:image/svg+xml,${encodeURIComponent(getPlaceholderSvg())}'"
                >
            </td>
            <td class="col-title">
                <a href="${escapeHtml(r.detail_url)}" target="_blank" rel="noopener noreferrer"
                   title="${escapeHtml(r.title)}">
                    ${escapeHtml(r.title)}
                </a>
            </td>
            <td class="col-date">${r.date}</td>
            <td class="col-pages">${r.images_count || '-'} 页</td>
            <td class="col-tags">
                ${r.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
            </td>
            <td class="col-action">
                <button class="btn-download" onclick="downloadReport(${r.id}, ${escapeJs(r.title)})">
                    <svg viewBox="0 0 14 14" fill="none">
                        <path d="M7 1v7.5M4 6l3 3 3-3M2 11h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    下载 PDF
                </button>
            </td>
        </tr>
    `).join('');
}

// ── 更新统计信息 ───────────────────────────────────────────

function updateStats(reports) {
    const count = reports.length;
    const totalPages = reports.reduce((sum, r) => sum + (r.images_count || 0), 0);

    // 动画计数
    animateNumber($totalCount, count);
    animateNumber($totalPages, totalPages);

    // 日期范围
    const sorted = [...reports].sort((a, b) => new Date(a.date) - new Date(b.date));
    const first = sorted[0]?.date?.slice(5) || '-';  // MM-DD
    const last = sorted[sorted.length - 1]?.date?.slice(5) || '-';
    $dateRange.textContent = `${first} ~ ${last}`;
}

function animateNumber(el, target) {
    const duration = 800;
    const start = performance.now();
    const initial = 0;

    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // easeOutExpo
        const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        const current = Math.round(initial + (target - initial) * eased);
        el.textContent = current.toLocaleString();
        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

// ── PDF 下载 ───────────────────────────────────────────────

async function downloadReport(productId, title) {
    if (isDownloading) return;
    isDownloading = true;

    showDownloadModal(title);

    try {
        // 1. 获取图片 URL
        updateProgress(5, '正在获取报告详情...');

        const detailResp = await fetch(`${API_BASE}/api/report/${productId}/detail`);
        if (!detailResp.ok) {
            const errData = await detailResp.json().catch(() => ({}));
            throw new Error(errData.error || `获取详情失败 (${detailResp.status})`);
        }

        const detailResult = await detailResp.json();
        if (!detailResult.success || !detailResult.data.image_urls?.length) {
            throw new Error(detailResult.error || '未找到报告图片');
        }

        const totalPages = detailResult.data.image_urls.length;
        updateProgress(15, `报告共 ${totalPages} 页，开始下载...`);
        $modalDetail.textContent = `报告：${title}`;

        // 2. 请求 PDF 生成（服务端下载图片 + 转换）
        // 使用 fetch 而非 window.open，以便处理进度和错误
        const downloadResp = await fetch(`${API_BASE}/api/report/${productId}/download`);

        if (!downloadResp.ok) {
            const errData = await downloadResp.json().catch(() => ({}));
            throw new Error(errData.error || `下载失败 (${downloadResp.status})`);
        }

        updateProgress(85, 'PDF 生成完成，正在下载...');

        // 3. 触发浏览器下载
        const blob = await downloadResp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${title}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        updateProgress(100, '下载完成!');

        // 短暂展示成功状态
        $progressFill.style.background = `linear-gradient(90deg, var(--success) 0%, #059669 100%)`;
        $modalCloseBtn.style.display = 'flex';

        setTimeout(() => hideDownloadModal(), 2500);

    } catch (err) {
        console.error('PDF 下载失败:', err);
        updateProgress(0, `错误: ${err.message}`);
        $progressFill.style.background = `linear-gradient(90deg, var(--error) 0%, #dc2626 100%)`;
        $modalCloseBtn.style.display = 'flex';
    } finally {
        isDownloading = false;
    }
}

// ── 进度管理 ───────────────────────────────────────────────

function updateProgress(percent, message) {
    const p = Math.max(0, Math.min(100, percent));
    $progressFill.style.width = `${p}%`;
    $progressText.textContent = message;
    $progressPercent.textContent = `${Math.round(p)}%`;
}

// ── UI 状态管理 ────────────────────────────────────────────

function showLoading() {
    $loading.style.display = 'flex';
}

function hideLoading() {
    $loading.style.display = 'none';
}

function showError(msg) {
    $errorMessage.textContent = msg;
    $errorPanel.style.display = 'flex';
}

function hideError() {
    $errorPanel.style.display = 'none';
}

function showStats() {
    $statsBar.style.display = 'grid';
}

function hideStats() {
    $statsBar.style.display = 'none';
}

function showTable() {
    $tableWrapper.style.display = 'block';
}

function hideTable() {
    $tableWrapper.style.display = 'none';
}

function showDownloadModal(title) {
    $modalTitle.textContent = '正在生成 PDF';
    $modalDetail.textContent = `报告：${title}`;
    $modalCloseBtn.style.display = 'none';
    $progressFill.style.width = '0%';
    $progressFill.style.background = `linear-gradient(90deg, var(--accent) 0%, #d4622b 100%)`;
    $progressText.textContent = '准备中...';
    $progressPercent.textContent = '0%';
    $downloadModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function hideDownloadModal() {
    $downloadModal.style.display = 'none';
    document.body.style.overflow = '';
}

// ── 工具函数 ───────────────────────────────────────────────

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function escapeJs(str) {
    if (!str) return "''";
    return `'${str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n')}'`;
}

function getPlaceholderSvg() {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="80" height="106" viewBox="0 0 80 106">
        <rect width="80" height="106" rx="4" fill="#191d29"/>
        <text x="40" y="50" text-anchor="middle" fill="#5a5f75" font-size="10" font-family="sans-serif">封面</text>
        <text x="40" y="65" text-anchor="middle" fill="#5a5f75" font-size="8" font-family="sans-serif">加载失败</text>
    </svg>`;
}

// ── 键盘快捷键 ─────────────────────────────────────────────
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        hideDownloadModal();
    }
});

// 点击模态框外部关闭
$downloadModal.addEventListener('click', (e) => {
    if (e.target === $downloadModal && !isDownloading) {
        hideDownloadModal();
    }
});
