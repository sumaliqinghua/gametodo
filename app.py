from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from tomatoes import TomatoTimer, record_tomato, show_today_stats, show_products
from Challenge import Challenge, load_challenges, create_random_challenge
from User import User
from product import Product, load_products, savejson, product_type_dict
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 初始化必要的对象
logger.info("Initializing application objects...")
tomato_timer = TomatoTimer()
challenges = load_challenges(is_active=True)
challenge = challenges[0] if challenges else create_random_challenge()
user = User()

@app.route('/')
def index():
    logger.debug("Serving index page")
    return render_template('index.html')

@app.route('/product')
def product():
    logger.debug("Serving product page")
    return render_template('product.html')

@app.route('/api/start-timer', methods=['POST'])
def start_timer():
    try:
        logger.debug("Starting timer")
        tomato_timer.start()
        return jsonify({"status": "success", "message": "Timer started"})
    except Exception as e:
        logger.error(f"Error starting timer: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stop-timer', methods=['POST'])
def stop_timer():
    try:
        logger.debug("Stopping timer")
        tomato_timer.stop()
        return jsonify({"status": "success", "message": "Timer stopped"})
    except Exception as e:
        logger.error(f"Error stopping timer: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/record-tomato', methods=['POST'])
def record_tomato():
    try:
        logger.debug("Recording tomato")
        data = request.json
        difficulty = data.get('difficulty', '中等')
        task = data.get('task', '工作')
        focus = int(data.get('focus', 2))
        achievement = float(data.get('achievement', 0.0))
        
        # 记录番茄钟
        result = record_tomatoes(
            user=user,  # 传递全局 user 对象
            difficulty=difficulty,
            task=task,
            focus=focus,
            achievement=achievement
        )
        
        return jsonify({
            "status": "success", 
            "message": "Tomato recorded",
            "result": result,
            "user_info": user.get_user_info()
        })
    except Exception as e:
        logger.error(f"Error recording tomato: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-stats')
def get_stats():
    try:
        if user is None:
            return jsonify({"status": "error", "message": "User not initialized"})
            
        stats = {
            "tomatoes_today": user.tomatoes_today,
            "total_tomatoes": user.tomatoes,
            "coins": user.coins,
            "continuous": user.continuous
        }
        return jsonify({"status": "success", "stats": stats})
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/get-challenges')
def get_challenges():
    try:
        challenges = load_challenges(True)
        if challenges is None:
            challenges = []
        return jsonify({
            "status": "success",
            "challenges": [c.__dict__ for c in challenges] if challenges else []
        })
    except Exception as e:
        logger.error(f"Error getting challenges: {str(e)}")
        return jsonify({"status": "success", "challenges": []})

@app.route('/api/get-user-info', methods=['GET'])
def get_user_info():
    try:
        logger.debug("Fetching user info")
        user_info = user.get_user_info()
        logger.debug(f"User info: {user_info}")
        return jsonify(user_info)
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get-products')
def get_products():
    try:
        products = show_products()
        logger.info(f"Products from show_products: {products}")  
        return jsonify({
            "status": "success",
            "products": products
        })
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}", exc_info=True)  
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/buy-product', methods=['POST'])
def buy_product():
    try:
        data = request.json
        product_name = data.get('product_name')
        
        # 检查产品是否存在并计算价格
        products = show_products()
        product = next((p for p in products if p['name'] == product_name), None)
        
        if not product:
            return jsonify({"status": "error", "message": "产品不存在"})
            
        if user.coins < product['price']:
            return jsonify({"status": "error", "message": "金币不足"})
            
        # 扣除金币
        user.coins -= product['price']
        user.save_user_data()
        
        return jsonify({
            "status": "success",
            "message": f"成功购买 {product_name}",
            "user_info": user.get_user_info()
        })
    except Exception as e:
        logger.error(f"Error buying product: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/get-purchased-products')
def get_purchased_products():
    try:
        products = load_products('json/purchased_product.json')
        products_data = []
        for product in products:
            product_data = {
                'name': product.name,
                'description': product.comments,
                'price': product.price,
                'type': product.type,
                'purchaseTime': product.purchaseTime,
                'writeoffTime': product.writeoffTime
            }
            products_data.append(product_data)
        return jsonify({
            "status": "success",
            "products": products_data
        })
    except Exception as e:
        logger.error(f"Error getting purchased products: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/add-product', methods=['POST'])
def add_product():
    try:
        data = request.json
        name = data.get('name')
        type_id = data.get('type')
        price = float(data.get('price'))
        discount = float(data.get('discount'))
        comments = data.get('comments', '')
        
        # 获取类型名称
        type_name = product_type_dict.get(str(type_id), '其他')
        
        # 创建新产品
        new_product = Product(
            name=name,
            price=price,
            type=type_name,
            discountCoefficient=discount,
            comments=comments
        )
        
        # 加载现有产品并添加新产品
        products = load_products()
        products.append(new_product)
        savejson('json/product.json', products)
        
        return jsonify({
            "status": "success",
            "message": "商品添加成功"
        })
    except Exception as e:
        logger.error(f"Error adding product: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
