// 工具函數

// 檢查是否已登入
function checkAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = '/frontend/pages/login.html';
        return false;
    }
    return true;
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 格式化相對時間
function formatRelativeTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days} 天前`;
    if (hours > 0) return `${hours} 小時前`;
    if (minutes > 0) return `${minutes} 分鐘前`;
    return '剛剛';
}

// 顯示錯誤訊息
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

// 顯示成功訊息
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);

    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// 顯示載入中
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-overlay';
    loadingDiv.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    loadingDiv.innerHTML = `
        <div class="bg-white rounded-lg p-6">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
    `;
    document.body.appendChild(loadingDiv);
}

// 隱藏載入中
function hideLoading() {
    const loadingDiv = document.getElementById('loading-overlay');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// 獲取狀態對應的中文
function getStatusText(status) {
    const statusMap = {
        // 辯論狀態
        'NEW': '新建',
        'ONGOING': '進行中',
        'FINISHED': '已結束',

        // 話題狀態
        'pending': '待審核',
        'approved': '已批准',
        'rejected': '已拒絕',

        // 回合狀態
        'WAIT_PROS_STATEMENT': '等待正方主張',
        'WAIT_CONS_QUESTIONS': '等待反方質詢',
        'WAIT_PROS_REPLY': '等待正方回覆',
        'WAIT_CONS_STATEMENT': '等待反方主張',
        'WAIT_PROS_QUESTIONS': '等待正方質詢',
        'WAIT_CONS_REPLY': '等待反方回覆',
        'WAIT_VOTING': '投票中',
        'VOTING_CLOSED': '投票已關閉',
        'ROUND_RESULT': '回合結束'
    };

    return statusMap[status] || status;
}

// 獲取狀態對應的顏色
function getStatusColor(status) {
    const colorMap = {
        'NEW': 'bg-blue-100 text-blue-800',
        'ONGOING': 'bg-green-100 text-green-800',
        'FINISHED': 'bg-gray-100 text-gray-800',
        'pending': 'bg-yellow-100 text-yellow-800',
        'approved': 'bg-green-100 text-green-800',
        'rejected': 'bg-red-100 text-red-800',
        'WAIT_VOTING': 'bg-purple-100 text-purple-800'
    };

    return colorMap[status] || 'bg-gray-100 text-gray-800';
}

// 渲染導航欄
function renderNavbar() {
    const user = getCurrentUser();
    const isLoggedIn = !!user;

    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    const navHTML = `
        <nav class="bg-white shadow-lg">
            <div class="container mx-auto px-4">
                <div class="flex justify-between items-center py-4">
                    <div class="flex items-center space-x-8">
                        <a href="/frontend/pages/index.html" class="text-2xl font-bold text-blue-600">辯論平台</a>
                        ${isLoggedIn ? `
                            <a href="/frontend/pages/debates.html" class="text-gray-700 hover:text-blue-600">辯論列表</a>
                            <a href="/frontend/pages/topics.html" class="text-gray-700 hover:text-blue-600">話題</a>
                            <a href="/frontend/pages/ranking.html" class="text-gray-700 hover:text-blue-600">排行榜</a>
                            ${user.is_admin ? '<a href="/frontend/pages/admin.html" class="text-gray-700 hover:text-blue-600">管理後台</a>' : ''}
                        ` : ''}
                    </div>
                    <div>
                        ${isLoggedIn ? `
                            <div class="flex items-center space-x-4">
                                <span class="text-gray-700">${user.nickname}</span>
                                <span class="text-sm text-gray-500">Rating: ${user.rating}</span>
                                <button onclick="AuthAPI.logout()" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">登出</button>
                            </div>
                        ` : `
                            <a href="/frontend/pages/login.html" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">登入</a>
                        `}
                    </div>
                </div>
            </div>
        </nav>
    `;

    navbar.innerHTML = navHTML;
}

// 初始化頁面
function initPage() {
    renderNavbar();
}
