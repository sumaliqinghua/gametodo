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

    // 开始计时器
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

    // 停止计时器
    stopButton.addEventListener('click', function() {
        if (isRunning) {
            fetch('/api/stop-timer', { method: 'POST' })
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

    // 记录番茄
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

    // 标签切换功能
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            
            // 更新按钮状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // 更新内容显示
            tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === tabId) {
                    pane.classList.add('active');
                }
            });
        });
    });

    // 聊天功能
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-message');
    const chatMessages = document.getElementById('chat-messages');

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    appendMessage('用户', message);
                    appendMessage('助手', data.response);
                    messageInput.value = '';
                }
            });
        }
    }

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

// 获取用户信息
function fetchUserInfo() {
    fetch('/api/get-user-info')
        .then(response => response.json())
        .then(data => {
            const userInfoDiv = document.getElementById('user-info');
            userInfoDiv.innerHTML = `
                <p>用户名: ${data.username}</p>
                <p>等级: ${data.level}</p>
                <p>金币: ${data.coins}</p>
            `;
        });
}

// 获取挑战列表
function fetchChallenges() {
    fetch('/api/get-challenges')
        .then(response => response.json())
        .then(challenges => {
            const challengesList = document.getElementById('challenges-list');
            challengesList.innerHTML = challenges.map(challenge => `
                <div class="challenge-card">
                    <h3>${challenge.name}</h3>
                    <p>${challenge.desc}</p>
                    <p>进度: ${challenge.progress}/${challenge.goal}</p>
                    <p>奖励: ${challenge.bonus} 金币</p>
                    <p>花费: ${challenge.cost} 金币</p>
                </div>
            `).join('');
        });
}

// 获取商品列表
function fetchProducts() {
    fetch('/api/get-products')
        .then(response => response.json())
        .then(products => {
            const productsList = document.getElementById('products-list');
            productsList.innerHTML = products.map(product => `
                <div class="product-card">
                    <h3>${product.name}</h3>
                    <p>${product.description}</p>
                    <p>价格: ${product.price} 金币</p>
                    <button onclick="purchaseProduct('${product.name}')">购买</button>
                </div>
            `).join('');
        });
}

// 购买商品
function purchaseProduct(productName) {
    fetch('/api/purchase-product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_name: productName })
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
    });
}
