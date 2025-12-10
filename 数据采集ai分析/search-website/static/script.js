// 分页状态管理
let currentPage = 1; // 当前页码
let isLoading = false; // 是否正在加载
let hasMore = true; // 是否还有更多数据

// 1. 搜索函数（支持分页和滚动加载）
async function search(reset = false) {
    // 重置分页状态（如果是新搜索）
    if (reset) {
        currentPage = 1;
        hasMore = true;
    }

    // 如果没有更多数据或正在加载，直接返回
    if (!hasMore || isLoading) return;

    const keyword = document.getElementById('keyword').value;
    const type = document.getElementById('type').value;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;
    const province = document.getElementById('province').value;
    const onlyImportant = document.getElementById('onlyImportant').checked;

    // 时间范围验证
    if (startTime && endTime && new Date(startTime) > new Date(endTime)) {
        showError('开始时间不能晚于截止时间');
        return;
    }

    // 构建请求参数（添加分页信息）
    const param = {
        keyword,
        type,
        province,
        onlyImportant,
        timeRange: {
            start: startTime,
            end: endTime
        },
        page: currentPage, // 当前页码
        page_size: 10      // 每页条数
    };

    try {
        isLoading = true;

        // 首次加载或重置时显示加载动画
        if (reset || currentPage === 1) {
            showLoading();
        } else {
            // 滚动加载时在底部添加加载提示
            appendLoadingIndicator();
        }

        // 发送请求到后端
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(param)
        });

        if (!response.ok) {
            throw new Error(`服务器响应错误: ${response.status}`);
        }

        const data = await response.json();

        // 更新分页状态
        hasMore = data.pagination.has_more;
        currentPage++;

        // 渲染结果（重置时覆盖，滚动加载时追加）
        renderResults(data, reset);
    } catch (error) {
        console.error('搜索失败:', error);
        showError('搜索失败，请重试');
    } finally {
        isLoading = false;
    }
}

// 2. 标签搜索函数（重置分页状态）
function searchByTag(tag) {
    document.getElementById('keyword').value = tag;
    document.getElementById('province').value = '';
    document.getElementById('onlyImportant').checked = false;
    document.getElementById('type').value = '';
    document.getElementById('startTime').value = '';
    document.getElementById('endTime').value = '';
    search(true); // 触发搜索并重置分页
}

// 3. 加载详情函数
function loadDetail(itemId) {
    if (!itemId || isNaN(itemId)) {
        showError('无效的项目ID');
        return;
    }
    window.open(`/api/item/${itemId}`, '_blank');
}

// 4. 渲染搜索结果
function renderResults(data, reset = false) {
    const contentArea = document.getElementById('contentArea');

    // 移除加载指示器
    const loader = document.getElementById('loading-indicator');
    if (loader) loader.remove();

    // 重置时清空内容区域
    if (reset) {
        contentArea.innerHTML = '';
    }

    // 获取当前筛选条件用于显示
    const keyword = document.getElementById('keyword').value;
    const type = document.getElementById('type').value;
    const province = document.getElementById('province').value;
    const onlyImportant = document.getElementById('onlyImportant').checked;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;

    // 构建筛选条件显示区域（仅在首次加载或重置时显示）
    if (reset || contentArea.innerHTML.trim() === '') {
        let filtersHtml = '<div class="filters mb-3 p-2 bg-light rounded">';
        filtersHtml += '<strong>当前筛选条件：</strong>';

        const filterItems = [];
        if (keyword) filterItems.push(`关键词: ${keyword}`);
        if (type) filterItems.push(`类型: ${type}`);
        if (province) filterItems.push(`省份: ${province}`);
        if (onlyImportant) filterItems.push('只显示重要信息');
        if (startTime || endTime) {
            const timeText = `${startTime || '开始'} - ${endTime || '现在'}`;
            filterItems.push(`时间: ${timeText}`);
        }

        filtersHtml += filterItems.length > 0 ? filterItems.join(' | ') : '无筛选条件（全部结果）';
        filtersHtml += ' <button class="btn btn-sm btn-outline-secondary ms-2" onclick="resetFilters()">重置</button>';
        filtersHtml += '</div>';

        if (data.results && data.results.length > 0) {
            contentArea.innerHTML += `
                <div class="mb-4">
                    <h1>搜索结果</h1>
                    <p class="text-muted">找到 ${data.pagination.total} 个结果</p>
                    ${filtersHtml}
                </div>
            `;
        } else {
            contentArea.innerHTML = `
                <div class="alert alert-info" role="alert">
                    <h4 class="alert-heading">没有找到结果</h4>
                    <p>请尝试更换关键词或调整筛选条件。</p>
                    ${filtersHtml}
                </div>
            `;
            return;
        }
    }

    // 渲染搜索结果（追加到现有内容后）
    if (data.results && data.results.length > 0) {
        const resultsContainer = document.createElement('div');
        resultsContainer.id = 'results-container';

        data.results.forEach(item => {
            const isImportant = item.isImportant;
            const importantClass = isImportant ? 'border-danger border-2' : '';

            const card = document.createElement('div');
            card.className = `card mb-3 result-card ${importantClass}`;
            card.onclick = () => loadDetail(item.id);

            card.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">
                        ${item.project_name}
                        <span class="project-code">| ${item.project_code}</span>
                    </h5>
                    <p class="card-text">
                        <strong>类型:</strong> ${item.type}
                        ${item.bidSort ? `<span class="text-muted">(${item.bidSort})</span>` : ''}
                    </p>
                    ${item.province ? `<p class="card-text"><strong>省份:</strong> ${item.province}</p>` : ''}
                    <p class="card-text"><strong>发布时间:</strong> ${item.time}</p>
                </div>
            `;

            resultsContainer.appendChild(card);
        });

        contentArea.appendChild(resultsContainer);

        // 如果没有更多数据，显示提示
        if (!hasMore) {
            const endMessage = document.createElement('div');
            endMessage.className = 'text-center text-muted py-4';
            endMessage.innerHTML = '已经到底啦~';
            contentArea.appendChild(endMessage);
        }
    }
}

// 5. 重置筛选条件
function resetFilters() {
    document.getElementById('keyword').value = '';
    document.getElementById('type').value = '';
    document.getElementById('startTime').value = '';
    document.getElementById('endTime').value = '';
    document.getElementById('province').value = '';
    document.getElementById('onlyImportant').checked = false;
    search(true); // 触发搜索并重置分页
}

// 6. 显示加载状态（修复：确保函数被定义）
function showLoading() {
    const contentArea = document.getElementById('contentArea');
    contentArea.innerHTML = `
        <div class="d-flex justify-content-center align-items-center" style="min-height: 50vh;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <span class="ms-3">加载中...</span>
        </div>
    `;
}

// 7. 显示错误提示（修复：确保函数被定义）
function showError(message) {
    const contentArea = document.getElementById('contentArea');
    contentArea.innerHTML = `
        <div class="mb-3">
            <button class="btn btn-secondary" onclick="history.back()">返回</button>
        </div>
        <div class="alert alert-danger" role="alert">
            <h4 class="alert-heading">错误</h4>
            <p>${message}</p>
        </div>
    `;
}

// 8. 滚动加载指示器
function appendLoadingIndicator() {
    const contentArea = document.getElementById('contentArea');
    const loader = document.createElement('div');
    loader.id = 'loading-indicator';
    loader.className = 'd-flex justify-content-center py-4';
    loader.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载更多...</span>
        </div>
        <span class="ms-3">加载更多...</span>
    `;
    contentArea.appendChild(loader);
}

// 9. 滚动监听函数
// 修复滚动加载的JavaScript代码
function handleScroll() {
    if (isLoading || !hasMore) return;

    // 获取内容区元素
    const contentArea = document.getElementById('contentArea');

    // 判断是否为小屏幕布局（侧边栏折叠）
    const isMobileLayout = window.innerWidth <= 768;

    let scrollTop, visibleHeight, contentHeight;

    if (isMobileLayout) {
        // 小屏幕：使用window滚动
        scrollTop = window.scrollY;
        visibleHeight = window.innerHeight;
        contentHeight = document.body.scrollHeight;
    } else {
        // 大屏幕：使用内容区内部滚动
        scrollTop = contentArea.scrollTop;
        visibleHeight = contentArea.clientHeight;
        contentHeight = contentArea.scrollHeight;
    }

    // 当滚动到距离底部200px时加载更多
    const bottomOfPage = scrollTop + visibleHeight >= contentHeight - 200;

    if (bottomOfPage) {
        search(false);
    }
}

// 修改DOMContentLoaded事件，监听内容区滚动而非window滚动
document.addEventListener('DOMContentLoaded', () => {
    // 搜索表单提交事件
    document.getElementById('searchForm').addEventListener('submit', (e) => {
        e.preventDefault();
        search(true);
    });

    // 重要信息复选框变更事件
    document.getElementById('onlyImportant').addEventListener('change', () => {
        search(true);
    });

    // 修改：根据屏幕尺寸监听不同的滚动事件
    function updateScrollListener() {
        // 先移除所有滚动监听
        window.removeEventListener('scroll', handleScroll);

        const contentArea = document.getElementById('contentArea');
        if (contentArea) {
            contentArea.removeEventListener('scroll', handleScroll);
        }

        // 根据屏幕尺寸添加适当的滚动监听
        if (window.innerWidth <= 768) {
            // 小屏幕：监听window滚动
            window.addEventListener('scroll', handleScroll);
        } else {
            // 大屏幕：监听内容区滚动
            if (contentArea) {
                contentArea.addEventListener('scroll', handleScroll);
            }
        }
    }

    // 初始化滚动监听
    updateScrollListener();

    // 窗口大小变化时重新设置滚动监听
    window.addEventListener('resize', updateScrollListener);

    // 初始加载
    search(true);
});