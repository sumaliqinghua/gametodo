# import datetime.datetime as data
from datetime import datetime
import json
import math
import os
import random
from Assitant.airequest import start_conversation
from Challenge import create_challenge, create_random_challenge, load_challenges, check_challenges
from User import User
from product import CanBuyOne, GotoStore, PurchaseProduct, RecordProduct, show_products
from recordLog import add_record, judge_record
from statics import record_all_tomatoes, show_today_stats
from utilsd import savejson
from flask import Flask, request, jsonify, render_template

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

app = Flask(__name__,
    template_folder=template_dir,
    static_folder=static_dir,
    static_url_path='/static'
)

# 基础配置
BASE_REWARD = 7 # 每个番茄钟的基础奖励
DAILY_GOAL = 8  # 每日目标番茄数
DAILY_REWARD = 5  # 达到每日目标的额外奖励
DECAY_AMOUNT = 50 # 达到此数值开始衰减
DECAY_RATE = 0.08

# 常量定义
TASK_TYPE = {
    '工作': 1.2,
    '爱好': 1.0,
    '杂事': 0.8,
    '番茄时间': 1.0
}

DIFFICULTY = {
    '简单': 0.8,
    '中等': 1.0,
    '困难': 1.2
}

FOCUS_LEVEL = {0:0.6, 1:0.8, 2:1.0, 3:1.2, 4:1.5}
Time_LEVEL = {0:0.6, 1:0.8, 2:1.0, 3:1.2, 4:1.5}

class TomatoTimer:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.user = User()

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = datetime.now()
            return True
        return False

    def stop(self):
        if self.running:
            self.running = False
            end_time = datetime.now()
            time_delta = (end_time - self.start_time).total_seconds() / 60
            if time_delta >= 25:
                coins = calculate_coins(self.user, "番茄时间", 1, time_delta)
                self.user.add_coins(coins)
                record_tomatoes(self.user)
            self.start_time = None
            return True
        return False

def calculate_coins(user, task_type, continuous_count=0, time_delta=0):
    reward = BASE_REWARD
    task_coeff = TASK_TYPE.get(task_type, 1.0)
    difficulty_coeff = DIFFICULTY.get(user.difficulty, 1.0)
    continuous_coeff = min(continuous_count * 0.1 + 1, 2)
    focus_coeff = 1 + getattr(user, 'focus', 0) * 0.1
    achievement_coeff = 1 + getattr(user, 'achievement', 0)
    
    reward *= task_coeff * difficulty_coeff * continuous_coeff * focus_coeff * achievement_coeff
    
    if time_delta > 60 * 3:  # 超过3小时
        decay = min((time_delta - 60 * 3) / (60 * 24), 0.5)  # 最多衰减50%
        reward *= (1 - decay)
    
    return round(reward, 2)

def handle_decay(user):
    try:
        if user.coins >= DECAY_AMOUNT:
            decay = user.coins * DECAY_RATE
            user.coins = round(user.coins - decay, 2)
            print(f"金币衰减: -{decay}")
    except Exception as e:
        print(f"Error handling decay: {str(e)}")

# Web Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def logs_page():
    return render_template('logs.html')

# API Routes
@app.route('/api/start-timer', methods=['POST'])
def start_timer_api():
    timer = TomatoTimer()
    if timer.start():
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Timer already running"})

@app.route('/api/stop-timer', methods=['POST'])
def stop_timer_api():
    timer = TomatoTimer()
    if timer.stop():
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Timer not running"})

@app.route('/api/get-user-info')
def get_user_info_api():
    try:
        user = User()
        user_info = {
            "tomatoes_today": getattr(user, 'tomatoes_today', 0),
            "tomatoes": getattr(user, 'tomatoes', 0),
            "continuous": getattr(user, 'continuous', 0),
            "coins": getattr(user, 'coins', 0),
            "gain": getattr(user, 'gain', 0)
        }
        return jsonify({"status": "success", "user_info": user_info})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-challenges')
def get_challenges_api():
    try:
        challenges = load_challenges()
        return jsonify({"status": "success", "challenges": challenges})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/get-stats')
def get_stats_api():
    try:
        stats = show_today_stats()
        return jsonify({"status": "success", "stats": stats})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/get-products')
def get_products_api():
    try:
        products = show_products()
        return jsonify({"status": "success", "products": products})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/add-log', methods=['POST'])
def add_log_api():
    data = request.json
    current_time = datetime.now()
    record = f"{current_time.year}年{current_time.month}月{current_time.day}日{current_time.hour}:{current_time.minute}:{current_time.second}\n"
    
    questions = ["1. 实际进度: ", "2. 困难/浪费: ", "3. 学到/收获: ", "4. 做得好的/不好的: ", "5. 改进措施: ", "6. 后续: ", "7. 鼓励: ", "8. 自我评分: "]
    
    for question in questions:
        answer = data.get(question.split('.')[1].strip().rstrip(':'), '')
        record += f"{question}{answer}\n"
    
    judegment = judge_record(record)
    record += f"9. AI点评: {judegment}\n"

    try:
        with open("recordLog.txt", "r+", encoding='utf-8') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(record + "\n" + content)
        return jsonify({"status": "success", "message": "日志已保存", "judgment": judegment})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/get-logs')
def get_logs_api():
    try:
        with open("recordLog.txt", "r", encoding='utf-8') as f:
            content = f.read()
        return jsonify({"status": "success", "logs": content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/record-tomato', methods=['POST'])
def record_tomato_api():
    try:
        data = request.json
        user = User()
        record_tomatoes(
            user,
            difficulty=data.get('difficulty'),
            task=data.get('task'),
            focus=int(data.get('focus', 2)),
            achievement=float(data.get('achievement', 0.5))
        )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/buy-product', methods=['POST'])
def buy_product_api():
    try:
        data = request.json
        product_name = data.get('product')
        if not product_name:
            return jsonify({"status": "error", "message": "Product name is required"})
        
        user = User()
        if PurchaseProduct(user, product_name):
            return jsonify({"status": "success", "message": f"Successfully purchased {product_name}"})
        else:
            return jsonify({"status": "error", "message": "Failed to purchase product"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)