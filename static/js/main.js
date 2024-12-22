document.addEventListener('DOMContentLoaded', function() {
    // 获取用户信息
    fetchUserInfo();
    // 获取挑战列表
    fetchChallenges();

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
function fetchChallenges() {
    fetch('/api/get-challenges')
        .then(response => response.json())
        .then(challenges => {
            const challengesList = document.getElementById('challenges-list');
            if (!Array.isArray(challenges)) {
                console.error('Challenges data is not an array:', challenges);
                return;
            }
            challengesList.innerHTML = challenges.map(challenge => `
                <div class="challenge-card">
                    <h3>${challenge.name}</h3>
                    <p>${challenge.desc}</p>
                    <p>目标: ${challenge.goal} 番茄</p>
                    <p>进度: ${challenge.progress}/${challenge.goal}</p>
                    <p>奖励: ${challenge.bonus}</p>
                    <p>花费: ${challenge.cost}</p>
                    ${challenge.failed ? '<p class="failed">已失败</p>' : ''}
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error fetching challenges:', error);
        });
}
