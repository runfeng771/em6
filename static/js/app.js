// 全局变量
let currentPage = 1;
let refreshInterval = null;
let keepAliveInterval = null;
let currentRefreshInterval = 10000; // 默认10秒

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    startKeepAlive();
});

// 初始化应用
function initializeApp() {
    loadAccounts();
    loadLogs();
    loadEmailConfig();
    loadSchedulerConfig();
    generateTimeOptions();
    
    // 绑定表单提交事件
    document.getElementById('emailConfigForm').addEventListener('submit', saveEmailConfig);
    document.getElementById('schedulerConfigForm').addEventListener('submit', saveSchedulerConfig);
    document.getElementById('addAccountForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addAccount();
    });
    document.getElementById('editAccountForm').addEventListener('submit', function(e) {
        e.preventDefault();
        updateAccount();
    });
}

// 加载账号列表
async function loadAccounts() {
    try {
        const response = await fetch('/api/accounts');
        const accounts = await response.json();
        
        const tbody = document.getElementById('accountsTableBody');
        tbody.innerHTML = '';
        
        accounts.forEach(account => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <span class="status-indicator ${account.login_status.toLowerCase()}"></span>
                    ${account.name}
                </td>
                <td>${account.account}</td>
                <td>
                    <span class="badge ${account.is_active ? 'bg-success' : 'bg-secondary'}">
                        ${account.is_active ? '启用' : '禁用'}
                    </span>
                </td>
                <td>${account.last_login ? new Date(account.last_login).toLocaleString() : '从未登录'}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-primary" onclick="manualLogin(${account.id})" title="手动登录">
                            <i class="fas fa-sign-in-alt"></i>
                        </button>
                        <button class="btn btn-warning" onclick="editAccount(${account.id})" title="编辑">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-danger" onclick="deleteAccount(${account.id})" title="删除">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // 更新定时任务信息
        updateSchedulerInfo();
    } catch (error) {
        console.error('加载账号失败:', error);
        Swal.fire('错误', '加载账号失败', 'error');
    }
}

// 加载日志
async function loadLogs() {
    try {
        const dateFilter = document.getElementById('dateFilter').value;
        const accountFilter = document.getElementById('accountFilter').value;
        const levelFilter = document.getElementById('levelFilter').value;
        
        const url = `/api/logs?page=${currentPage}&per_page=50&date=${dateFilter}&account=${accountFilter}&level=${levelFilter}`;
        const response = await fetch(url);
        const data = await response.json();
        
        // 更新日志计数
        document.getElementById('logCount').textContent = `共 ${data.total} 条日志`;
        
        // 更新分页按钮
        document.getElementById('prevBtn').disabled = currentPage <= 1;
        document.getElementById('nextBtn').disabled = currentPage >= data.pages;
        
        // 显示日志
        const container = document.getElementById('logsContainer');
        container.innerHTML = '';
        
        if (data.logs.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-5">暂无日志数据</div>';
            return;
        }
        
        data.logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log.level}`;
            logEntry.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${log.account_name}</strong>
                        <span class="badge bg-secondary ms-2">${log.level}</span>
                        <small class="text-muted ms-2">${new Date(log.timestamp).toLocaleString()}</small>
                    </div>
                </div>
                <div class="mt-2">${log.message}</div>
            `;
            container.appendChild(logEntry);
        });
        
        // 滚动到顶部
        container.scrollTop = 0;
        
        // 加载过滤选项
        if (document.getElementById('dateFilter').options.length === 1) {
            await loadFilterOptions();
        }
    } catch (error) {
        console.error('加载日志失败:', error);
        document.getElementById('logsContainer').innerHTML = '<div class="text-center text-danger py-5">加载日志失败</div>';
    }
}

// 加载过滤选项
async function loadFilterOptions() {
    try {
        // 获取所有日志来提取过滤选项
        const response = await fetch('/api/logs?per_page=1000');
        const data = await response.json();
        
        // 获取唯一日期
        const dates = [...new Set(data.logs.map(log => log.date))].sort().reverse();
        const dateSelect = document.getElementById('dateFilter');
        dates.forEach(date => {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = date;
            dateSelect.appendChild(option);
        });
        
        // 获取唯一账号
        const accounts = [...new Set(data.logs.map(log => log.account_name))];
        const accountSelect = document.getElementById('accountFilter');
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account;
            option.textContent = account;
            accountSelect.appendChild(option);
        });
    } catch (error) {
        console.error('加载过滤选项失败:', error);
    }
}

// 刷新日志
function refreshLogs() {
    showRefreshIndicator();
    loadLogs();
}

// 清空日志
async function clearLogs() {
    const result = await Swal.fire({
        title: '确认清空',
        text: '确定要清空日志吗？此操作不可恢复。',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
    });
    
    if (result.isConfirmed) {
        try {
            const dateFilter = document.getElementById('dateFilter').value;
            const response = await fetch('/api/logs/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ date: dateFilter })
            });
            
            if (response.ok) {
                Swal.fire('成功', '日志已清空', 'success');
                refreshLogs();
            } else {
                Swal.fire('错误', '清空日志失败', 'error');
            }
        } catch (error) {
            console.error('清空日志失败:', error);
            Swal.fire('错误', '清空日志失败', 'error');
        }
    }
}

// 改变刷新间隔
function changeRefreshInterval() {
    const interval = parseInt(document.getElementById('refreshInterval').value);
    currentRefreshInterval = interval * 1000;
    
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    
    if (interval > 0) {
        startAutoRefresh();
    }
    
    hideRefreshIndicator();
}

// 开始自动刷新
function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    if (currentRefreshInterval > 0) {
        refreshInterval = setInterval(() => {
            if (document.getElementById('logs-tab').classList.contains('active')) {
                refreshLogs();
            }
        }, currentRefreshInterval);
        
        showRefreshIndicator();
    }
}

// 显示刷新指示器
function showRefreshIndicator() {
    if (currentRefreshInterval > 0) {
        document.getElementById('refreshIndicator').style.display = 'block';
    }
}

// 隐藏刷新指示器
function hideRefreshIndicator() {
    document.getElementById('refreshIndicator').style.display = 'none';
}

// 分页功能
function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        refreshLogs();
    }
}

function nextPage() {
    currentPage++;
    refreshLogs();
}

// 显示添加账号模态框
function showAddAccountModal() {
    const modal = new bootstrap.Modal(document.getElementById('addAccountModal'));
    modal.show();
}

// 添加账号
async function addAccount() {
    const name = document.getElementById('accountName').value;
    const account = document.getElementById('accountEmail').value;
    const password = document.getElementById('accountPassword').value;
    
    try {
        const response = await fetch('/api/accounts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, account, password })
        });
        
        if (response.ok) {
            Swal.fire('成功', '账号添加成功', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addAccountModal')).hide();
            document.getElementById('addAccountForm').reset();
            loadAccounts();
        } else {
            Swal.fire('错误', '添加账号失败', 'error');
        }
    } catch (error) {
        console.error('添加账号失败:', error);
        Swal.fire('错误', '添加账号失败', 'error');
    }
}

// 编辑账号
async function editAccount(id) {
    try {
        const response = await fetch('/api/accounts');
        const accounts = await response.json();
        const account = accounts.find(a => a.id === id);
        
        if (account) {
            document.getElementById('editAccountId').value = account.id;
            document.getElementById('editAccountName').value = account.name;
            document.getElementById('editAccountEmail').value = account.account;
            document.getElementById('editAccountPassword').value = account.password;
            document.getElementById('editAccountActive').checked = account.is_active;
            
            const modal = new bootstrap.Modal(document.getElementById('editAccountModal'));
            modal.show();
        }
    } catch (error) {
        console.error('加载账号信息失败:', error);
        Swal.fire('错误', '加载账号信息失败', 'error');
    }
}

// 更新账号
async function updateAccount() {
    const id = document.getElementById('editAccountId').value;
    const name = document.getElementById('editAccountName').value;
    const account = document.getElementById('editAccountEmail').value;
    const password = document.getElementById('editAccountPassword').value;
    const is_active = document.getElementById('editAccountActive').checked;
    
    try {
        const response = await fetch(`/api/accounts/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, account, password, is_active })
        });
        
        if (response.ok) {
            Swal.fire('成功', '账号更新成功', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editAccountModal')).hide();
            loadAccounts();
        } else {
            Swal.fire('错误', '更新账号失败', 'error');
        }
    } catch (error) {
        console.error('更新账号失败:', error);
        Swal.fire('错误', '更新账号失败', 'error');
    }
}

// 删除账号
async function deleteAccount(id) {
    const result = await Swal.fire({
        title: '确认删除',
        text: '确定要删除这个账号吗？',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
    });
    
    if (result.isConfirmed) {
        try {
            const response = await fetch(`/api/accounts/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                Swal.fire('成功', '账号删除成功', 'success');
                loadAccounts();
            } else {
                Swal.fire('错误', '删除账号失败', 'error');
            }
        } catch (error) {
            console.error('删除账号失败:', error);
            Swal.fire('错误', '删除账号失败', 'error');
        }
    }
}

// 手动登录
async function manualLogin(id) {
    try {
        const response = await fetch(`/api/accounts/${id}/login`, {
            method: 'POST'
        });
        
        if (response.ok) {
            Swal.fire('成功', '登录任务已启动，请查看日志', 'success');
            // 切换到日志标签页
            document.getElementById('logs-tab').click();
            startAutoRefresh();
        } else {
            Swal.fire('错误', '启动登录任务失败', 'error');
        }
    } catch (error) {
        console.error('手动登录失败:', error);
        Swal.fire('错误', '启动登录任务失败', 'error');
    }
}

// 执行所有账号登录
async function runAllAccounts() {
    const result = await Swal.fire({
        title: '确认执行',
        text: '确定要执行所有账号的登录任务吗？',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
    });
    
    if (result.isConfirmed) {
        try {
            const response = await fetch('/api/accounts');
            const accounts = await response.json();
            
            let successCount = 0;
            for (const account of accounts) {
                if (account.is_active) {
                    const loginResponse = await fetch(`/api/accounts/${account.id}/login`, {
                        method: 'POST'
                    });
                    if (loginResponse.ok) {
                        successCount++;
                    }
                }
            }
            
            Swal.fire('成功', `已启动 ${successCount} 个账号的登录任务`, 'success');
            // 切换到日志标签页
            document.getElementById('logs-tab').click();
            startAutoRefresh();
        } catch (error) {
            console.error('执行所有账号登录失败:', error);
            Swal.fire('错误', '执行所有账号登录失败', 'error');
        }
    }
}

// 加载邮件配置
async function loadEmailConfig() {
    try {
        const response = await fetch('/api/email_config');
        const config = await response.json();
        
        if (config.smtp_server) {
            document.getElementById('smtpServer').value = config.smtp_server;
            document.getElementById('smtpPort').value = config.smtp_port;
            document.getElementById('senderEmail').value = config.sender_email;
            document.getElementById('senderPassword').value = config.sender_password;
            document.getElementById('receiverEmail').value = config.receiver_email;
            document.getElementById('emailEnabled').checked = config.is_active;
        }
    } catch (error) {
        console.error('加载邮件配置失败:', error);
    }
}

// 保存邮件配置
async function saveEmailConfig(e) {
    e.preventDefault();
    
    const config = {
        smtp_server: document.getElementById('smtpServer').value,
        smtp_port: parseInt(document.getElementById('smtpPort').value),
        sender_email: document.getElementById('senderEmail').value,
        sender_password: document.getElementById('senderPassword').value,
        receiver_email: document.getElementById('receiverEmail').value,
        is_active: document.getElementById('emailEnabled').checked
    };
    
    try {
        const response = await fetch('/api/email_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            Swal.fire('成功', '邮件配置保存成功', 'success');
        } else {
            Swal.fire('错误', '保存邮件配置失败', 'error');
        }
    } catch (error) {
        console.error('保存邮件配置失败:', error);
        Swal.fire('错误', '保存邮件配置失败', 'error');
    }
}

// 加载定时任务配置
async function loadSchedulerConfig() {
    try {
        const response = await fetch('/api/scheduler_config');
        const config = await response.json();
        
        if (config.hour1 !== undefined) {
            document.getElementById('hour1').value = config.hour1;
            document.getElementById('minute1').value = config.minute1;
            document.getElementById('hour2').value = config.hour2;
            document.getElementById('minute2').value = config.minute2;
            document.getElementById('schedulerEnabled').checked = config.is_enabled;
        }
    } catch (error) {
        console.error('加载定时任务配置失败:', error);
    }
}

// 保存定时任务配置
async function saveSchedulerConfig(e) {
    e.preventDefault();
    
    const config = {
        hour1: parseInt(document.getElementById('hour1').value),
        minute1: parseInt(document.getElementById('minute1').value),
        hour2: parseInt(document.getElementById('hour2').value),
        minute2: parseInt(document.getElementById('minute2').value),
        is_enabled: document.getElementById('schedulerEnabled').checked
    };
    
    try {
        const response = await fetch('/api/scheduler_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            Swal.fire('成功', '定时任务配置保存成功', 'success');
            updateSchedulerInfo();
        } else {
            Swal.fire('错误', '保存定时任务配置失败', 'error');
        }
    } catch (error) {
        console.error('保存定时任务配置失败:', error);
        Swal.fire('错误', '保存定时任务配置失败', 'error');
    }
}

// 生成时间选项
function generateTimeOptions() {
    const hourSelects = ['hour1', 'hour2'];
    const minuteSelects = ['minute1', 'minute2'];
    
    // 生成小时选项
    hourSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        for (let i = 0; i < 24; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = i.toString().padStart(2, '0');
            select.appendChild(option);
        }
    });
    
    // 生成分钟选项
    minuteSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        for (let i = 0; i < 60; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = i.toString().padStart(2, '0');
            select.appendChild(option);
        }
    });
}

// 更新定时任务信息
async function updateSchedulerInfo() {
    try {
        const response = await fetch('/api/scheduler_config');
        const config = await response.json();
        
        const infoDiv = document.getElementById('schedulerInfo');
        if (config.is_enabled) {
            infoDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    定时任务已启用
                </div>
                <div class="mt-3">
                    <h6>执行时间：</h6>
                    <ul class="list-unstyled">
                        <li><i class="fas fa-clock me-2"></i>${config.hour1.toString().padStart(2, '0')}:${config.minute1.toString().padStart(2, '0')}</li>
                        <li><i class="fas fa-clock me-2"></i>${config.hour2.toString().padStart(2, '0')}:${config.minute2.toString().padStart(2, '0')}</li>
                    </ul>
                </div>
            `;
        } else {
            infoDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    定时任务已禁用
                </div>
            `;
        }
    } catch (error) {
        console.error('更新定时任务信息失败:', error);
    }
}

// 启动保活机制
function startKeepAlive() {
    // 每20秒发送一次保活请求
    keepAliveInterval = setInterval(() => {
        fetch('/api/keep_alive')
            .then(response => response.json())
            .then(data => {
                console.log('保活请求:', data);
            })
            .catch(error => {
                console.error('保活请求失败:', error);
            });
    }, 20000);
}

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    if (keepAliveInterval) {
        clearInterval(keepAliveInterval);
    }
});