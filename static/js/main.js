document.addEventListener('DOMContentLoaded', function() {
    // 获取用户信息
    fetchUserInfo();
    // 获取挑战列表
    fetchChallenges();
    // 获取统计信息
    fetchStats();

    // 定时器相关元素
    const timerDisplay = document.getElementById('timer');
    const startButton = document.getElementById('start-timer');
    const stopButton = document.getElementById('stop-timer');

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
            `;
        });
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
async function recordTomato() {
    const difficulty = document.getElementById('difficulty').value;
    const task = document.getElementById('task').value;
    const focus = parseInt(document.getElementById('focus').value);
    const achievement = parseFloat(document.getElementById('achievement').value);

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
            alert(`记录成功！获得 ${data.result.coins_earned} 金币`);
            updateUserInfo(data.user_info);
            fetchStats();  // 更新统计信息
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        console.error('Error recording tomato:', error);
        alert('记录失败：' + error.message);
    }
}

// 获取统计信息
async function fetchStats() {
    try {
        const response = await fetch('/api/get-stats');
        const data = await response.json();
        
        if (data.status === 'success' && data.stats) {
            const statsDiv = document.getElementById('stats');
            if (!statsDiv) return;

            statsDiv.innerHTML = `
                <h2>今日统计</h2>
                <p>今日番茄数：${data.stats.tomatoes_today}</p>
                <p>总番茄数：${data.stats.total_tomatoes}</p>
                <p>连续番茄数：${data.stats.continuous}</p>
                <p>当前金币：${data.stats.coins.toFixed(2)}</p>
            `;
        } else {
            console.error('Failed to fetch stats:', data.message);
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// 更新用户信息显示
function updateUserInfo(userInfo) {
    const userInfoDiv = document.getElementById('user-info');
    if (!userInfoDiv) return;

    userInfoDiv.innerHTML = `
        <p>总番茄数：${userInfo.tomatoes}</p>
        <p>今日番茄数：${userInfo.tomatoes_today}</p>
        <p>连续番茄数：${userInfo.continuous}</p>
        <p>金币：${userInfo.coins.toFixed(2)}</p>
        <p>上次获得：${userInfo.gain}</p>
    `;
}
