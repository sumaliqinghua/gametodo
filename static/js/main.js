// 全局变量
let userInfo = null;

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 获取用户信息
    updateUserInfo();

    // 根据当前页面初始化不同功能
    if (window.location.pathname === '/') {
        // 主页功能
        initMainPage();
    } else if (window.location.pathname === '/logs') {
        // 日志页功能
        initLogsPage();
    }
});

// 主页初始化
function initMainPage() {
    // 获取挑战列表
    fetchChallenges();
    // 获取统计信息
    fetchStats();
    // 获取商品列表
    fetchProducts();

    // 定时器相关元素
    const timerDisplay = document.getElementById('timer');
    const startButton = document.getElementById('start-timer');
    const stopButton = document.getElementById('stop-timer');

    if (timerDisplay && startButton && stopButton) {
        // 计时器状态
        let isRunning = false;
        let timeLeft = 25 * 60; // 25分钟，以秒为单位

        // 开始计时器
        startButton.addEventListener('click', function() {
            if (!isRunning) {
                fetch('/api/start-timer', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        isRunning = true;
                        startTimer();
                    }
                });
            }
        });

        // 停止计时器
        stopButton.addEventListener('click', function() {
            if (isRunning) {
                fetch('/api/stop-timer', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        isRunning = false;
                        timeLeft = 25 * 60;
                        updateTimerDisplay();
                    }
                });
            }
        });

        // 更新计时器显示
        function updateTimerDisplay() {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }

        // 启动计时器
        function startTimer() {
            if (isRunning) {
                if (timeLeft > 0) {
                    timeLeft--;
                    updateTimerDisplay();
                    setTimeout(startTimer, 1000);
                } else {
                    isRunning = false;
                    alert('时间到！');
                    timeLeft = 25 * 60;
                    updateTimerDisplay();
                }
            }
        }
    }
}

// 日志页初始化
function initLogsPage() {
    // 获取日志记录
    fetchLogs();
}

// 更新用户信息
async function updateUserInfo() {
    try {
        const response = await fetch('/api/get-user-info');
        const data = await response.json();
        
        if (data.status === 'success') {
            userInfo = data.user_info;  // 保存用户信息
            const userInfoDiv = document.getElementById('user-info');
            if (!userInfoDiv) return;

            userInfoDiv.innerHTML = `
                <p>今日番茄：${userInfo.tomatoes_today}</p>
                <p>总番茄数：${userInfo.tomatoes}</p>
                <p>连续番茄：${userInfo.continuous}</p>
                <p>金币：${userInfo.coins.toFixed(2)}</p>
                <p>上次获得：${userInfo.gain}</p>
            `;
            
            // 更新商品列表（因为金币数可能影响购买按钮状态）
            fetchProducts();
        }
    } catch (error) {
        console.error('Error updating user info:', error);
    }
}

// 获取挑战列表
async function fetchChallenges() {
    try {
        const response = await fetch('/api/get-challenges');
        const data = await response.json();
        
        if (data.status === 'success') {
            const challengesList = document.getElementById('challenges-list');
            if (!challengesList) return;

            if (!data.challenges || data.challenges.length === 0) {
                challengesList.innerHTML = '<p>当前没有活跃的挑战</p>';
                return;
            }

            const challengesHtml = data.challenges.map(challenge => `
                <div class="challenge-item">
                    <h3>${challenge.name}</h3>
                    <p>${challenge.desc[challenge.progress || 0]}</p>
                    <p>目标：${challenge.goal} 番茄钟</p>
                    <p>奖励：${challenge.bonus} 金币</p>
                    <p>进度：${challenge.progress || 0}/${challenge.goal}</p>
                </div>
            `).join('');

            challengesList.innerHTML = challengesHtml;
        } else {
            console.error('Failed to fetch challenges:', data.message);
        }
    } catch (error) {
        console.error('Error fetching challenges:', error);
    }
}

// 记录番茄钟
async function recordTomato(difficulty, task, focus, achievement) {
    try {
        const response = await fetch('/api/record-tomato', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                difficulty,
                task,
                focus,
                achievement
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            // 更新统计信息
            updateStats({
                tomatoes_today: userInfo.tomatoes_today + 1,
                total_tomatoes: userInfo.tomatoes + 1,
                continuous_count: data.data.continuous_count,
                coins: data.data.total_coins
            });
            
            // 更新用户信息
            await updateUserInfo();
            
            alert(`成功记录番茄！获得 ${data.data.coins_earned} 金币`);
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error recording tomato:', error);
        alert('记录番茄失败：' + error.message);
    }
}

// 获取统计信息
async function fetchStats() {
    try {
        const response = await fetch('/api/get-stats');
        const data = await response.json();
        if (data.status === 'success') {
            updateStats(data.stats);
        } else {
            console.error('Failed to fetch stats:', data.message);
        }
    } catch (error) {
        console.error('Failed to fetch stats:', error);
    }
}

// 更新统计信息显示
function updateStats(stats) {
    const statsContainer = document.getElementById('stats');
    if (statsContainer) {
        statsContainer.innerHTML = `
            <p>今日番茄数：${stats.tomatoes_today || 0}</p>
            <p>总番茄数：${stats.total_tomatoes || 0}</p>
            <p>连续番茄数：${stats.continuous_count || 0}</p>
            <p>金币：${stats.coins || 0}</p>
        `;
    }
}

// 获取商品列表
async function fetchProducts() {
    try {
        const response = await fetch('/api/get-products');
        const data = await response.json();
        console.log('Products data:', data);
        
        if (data.status === 'success') {
            const productsList = document.getElementById('products-list');
            if (!productsList) return;

            if (!data.products || data.products.length === 0) {
                productsList.innerHTML = '<p>暂无商品</p>';
                return;
            }

            const productsHtml = data.products.map(product => {
                const hasDiscount = product.discountCoefficient < 1.0;
                const priceDisplay = hasDiscount ? 
                    `<p class="price">
                        <span class="original-price">原价：${product.price} 金币</span>
                        <span class="discount-price">折扣价：${product.discountPrice} 金币</span>
                        <span class="discount-rate">(${(product.discountCoefficient * 100).toFixed(0)}折)</span>
                    </p>` :
                    `<p class="price">价格：${product.price} 金币</p>`;

                return `
                    <div class="product-item ${hasDiscount ? 'has-discount' : ''}">
                        <h3>${product.name}</h3>
                        <p class="type">类型：${product.type}</p>
                        <p>${product.description || ''}</p>
                        ${priceDisplay}
                        <button onclick="buyProduct('${product.name}')" 
                                ${!userInfo || userInfo.coins < (hasDiscount ? product.discountPrice : product.price) ? 'disabled' : ''}>
                            购买
                        </button>
                    </div>
                `;
            }).join('');

            productsList.innerHTML = productsHtml;
        } else {
            console.error('Failed to fetch products:', data.message);
        }
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

// 购买商品
async function buyProduct(productName) {
    try {
        const response = await fetch('/api/buy-product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_name: productName
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            alert(data.message);
            updateUserInfo();
            fetchProducts();  // 刷新商品列表
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error buying product:', error);
        alert('购买失败：' + error.message);
    }
}

// 获取日志记录
async function fetchLogs() {
    try {
        const response = await fetch('/api/get-logs');
        const data = await response.json();
        
        if (data.status === 'success') {
            const logsDiv = document.getElementById('logs-container');
            if (!logsDiv) return;
            
            // 将日志文本转换为HTML格式
            const logsHtml = data.logs.split('\n').map(line => 
                `<div class="log-line">${line}</div>`
            ).join('');
            
            logsDiv.innerHTML = logsHtml;
        }
    } catch (error) {
        console.error('获取日志失败:', error);
    }
}

// 提交日志
async function submitLog() {
    const logData = {
        '实际进度': document.getElementById('progress').value,
        '困难/浪费': document.getElementById('difficulties').value,
        '学到/收获': document.getElementById('learnings').value,
        '做得好的/不好的': document.getElementById('evaluation').value,
        '改进措施': document.getElementById('improvements').value,
        '后续': document.getElementById('next-steps').value,
        '鼓励': document.getElementById('encouragement').value,
        '自我评分': document.getElementById('self-score').value
    };

    try {
        const response = await fetch('/api/add-log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(logData)
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            alert('日志保存成功！\nAI点评：' + data.judgment);
            // 清空输入框
            Object.keys(logData).forEach(key => {
                document.getElementById(key.toLowerCase().replace(/[\/\s]/g, '-')).value = '';
            });
            // 刷新日志显示
            fetchLogs();
        } else {
            alert('保存失败：' + data.message);
        }
    } catch (error) {
        console.error('提交日志失败:', error);
        alert('提交失败，请重试');
    }
}
