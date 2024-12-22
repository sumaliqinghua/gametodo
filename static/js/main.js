document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面数据
    fetchUserInfo();
    fetchChallenges();
    fetchProducts();

    // 定时器相关元素
    const timerDisplay = document.getElementById('timer');
    const startButton = document.getElementById('start-timer');
    const stopButton = document.getElementById('stop-timer');
    const recordButton = document.getElementById('record-tomato');

    // 计时器状态
    let isRunning = false;
    let timeLeft = 25 * 60; // 25分钟，以秒为单位

    // 只有在元素存在时才添加事件监听器
    if (startButton) {
        startButton.addEventListener('click', function() {
            if (!isRunning) {
                fetch('/api/start-timer', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            isRunning = true;
                            startTimer();
                        }
                    });
            }
        });
    }

    if (stopButton) {
        stopButton.addEventListener('click', function() {
            if (isRunning) {
                fetch('/api/stop-timer', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            isRunning = false;
                            clearInterval(timerInterval);
                        }
                    });
            }
        });
    }

    if (recordButton) {
        recordButton.addEventListener('click', function() {
            fetch('/api/record-tomato', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('番茄记录成功！');
                        fetchUserInfo(); // 更新用户信息
                    } else {
                        alert('记录失败：' + data.message);
                    }
                });
        });
    }

    let timerInterval;
    function startTimer() {
        timerInterval = setInterval(() => {
            if (timeLeft > 0) {
                timeLeft--;
                updateTimerDisplay();
            } else {
                clearInterval(timerInterval);
                isRunning = false;
                alert('时间到！');
            }
        }, 1000);
    }

    function updateTimerDisplay() {
        if (timerDisplay) {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    // 标签切换功能
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有标签的active类
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            // 添加当前标签的active类
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // 初始化显示
    updateTimerDisplay();
});

// 获取用户信息
function fetchUserInfo() {
    fetch('/api/get-user-info')
        .then(response => response.json())
        .then(data => {
            const userInfoDiv = document.getElementById('user-info');
            if (userInfoDiv) {
                userInfoDiv.innerHTML = `
                    <p>用户名: ${data.username}</p>
                    <p>等级: ${data.level}</p>
                    <p>金币: ${data.coins}</p>
                    <p>番茄数: ${data.tomatoes}</p>
                    <p>今日番茄: ${data.tomatoes_today}</p>
                    <p>连续完成: ${data.continuous}</p>
                    <p>成就值: ${data.achievement}</p>
                `;
            }
        })
        .catch(error => console.error('Error fetching user info:', error));
}

// 获取挑战列表
function fetchChallenges() {
    fetch('/api/get-challenges')
        .then(response => response.json())
        .then(data => {
            const challengesDiv = document.getElementById('challenges-list');
            if (challengesDiv) {
                challengesDiv.innerHTML = data.map(challenge => `
                    <div class="challenge-item ${challenge.completed ? 'completed' : ''}">
                        <h3>${challenge.name}</h3>
                        <p>${challenge.description}</p>
                        <p>奖励: ${challenge.reward} 金币</p>
                    </div>
                `).join('');
            }
        })
        .catch(error => console.error('Error fetching challenges:', error));
}

// 获取商品列表
function fetchProducts() {
    fetch('/api/get-products')
        .then(response => response.json())
        .then(data => {
            const productsDiv = document.getElementById('products-list');
            if (productsDiv) {
                productsDiv.innerHTML = data.map(product => `
                    <div class="product-item">
                        <h3>${product.name}</h3>
                        <p>${product.description}</p>
                        <p>价格: ${product.price} 金币</p>
                        <p>折扣: ${product.discount * 100}%</p>
                        <button onclick="purchaseProduct('${product.name}')">购买</button>
                    </div>
                `).join('');
            }
        })
        .catch(error => console.error('Error fetching products:', error));
}

// 购买商品
function purchaseProduct(productName) {
    fetch('/api/purchase-product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ productName: productName })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('购买成功！');
                fetchUserInfo(); // 更新用户信息
                fetchProducts(); // 更新商品列表
            } else {
                alert('购买失败：' + data.message);
            }
        })
        .catch(error => console.error('Error purchasing product:', error));
}
