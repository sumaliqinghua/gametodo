from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from tomatoes import TomatoTimer, record_tomatoes, handle_decay
from Challenge import Challenge, load_challenges, create_random_challenge, check_challenges
from User import User
from product import show_products, PurchaseProduct
from Assitant.airequest import start_conversation
import json

app = Flask(__name__)
CORS(app)

# 禁用缓存
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

# 初始化必要的对象
tomato_timer = TomatoTimer()
challenges = load_challenges(is_active=True)
challenge = challenges[0] if challenges else create_random_challenge()
user = User()  # 使用默认参数创建用户

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    response = send_from_directory('static', filename)
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/api/start-timer', methods=['POST'])
def start_timer():
    tomato_timer.start()
    return jsonify({"status": "success", "message": "Timer started"})

@app.route('/api/stop-timer', methods=['POST'])
def stop_timer():
    tomato_timer.stop()
    return jsonify({"status": "success", "message": "Timer stopped"})

@app.route('/api/record-tomato', methods=['POST'])
def record_tomato():
    try:
        record_tomatoes()
        handle_decay()  # 处理金币衰减
        return jsonify({"status": "success", "message": "Tomato recorded successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/get-user-info', methods=['GET'])
def get_user_info():
    try:
        return jsonify(user.get_user_info())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-challenges', methods=['GET'])
def get_challenges():
    try:
        challenges_list = []
        for challenge in challenges:
            challenges_list.append({
                'name': challenge.name,
                'description': challenge.desc,
                'reward': challenge.bonus,
                'completed': challenge.progress >= challenge.goal
            })
        return jsonify(challenges_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-products', methods=['GET'])
def get_products():
    try:
        products_list = show_products()
        return jsonify(products_list)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/purchase-product', methods=['POST'])
def purchase_product():
    try:
        data = request.get_json()
        if not data or 'productName' not in data:
            return jsonify({"status": "error", "message": "Product name is required"}), 400
        
        result = PurchaseProduct(user.coins)
        if result[0] >= 0:
            user.coins = result[0]
            return jsonify({"status": "success", "message": f"Successfully purchased {result[1]}"})
        else:
            return jsonify({"status": "error", "message": "Not enough coins"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"status": "error", "message": "Message is required"}), 400
        
        response = start_conversation(data['message'])
        return jsonify({"status": "success", "message": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
