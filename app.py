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
user = User()

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

@app.route('/api/get-challenges', methods=['GET'])
def get_challenges():
    active_challenges = load_challenges(is_active=True)
    check_challenges(active_challenges, user)  # 检查挑战完成情况
    return jsonify([c.tojson() for c in active_challenges])

@app.route('/api/get-user-info', methods=['GET'])
def get_user_info():
    user_info = user.get_user_info()
    return jsonify(user_info)

@app.route('/api/get-products', methods=['GET'])
def get_products():
    products = show_products()
    return jsonify(products)

@app.route('/api/purchase-product', methods=['POST'])
def purchase_product():
    data = request.json
    product_name = data.get('product_name')
    try:
        PurchaseProduct(product_name)
        return jsonify({"status": "success", "message": "Product purchased successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    try:
        response = start_conversation(message)
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
