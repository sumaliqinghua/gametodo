from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from tomatoes import TomatoTimer
from Challenge import Challenge, load_challenges, create_random_challenge
from User import User
import json

app = Flask(__name__)
CORS(app)

# 初始化必要的对象
tomato_timer = TomatoTimer()
challenges = load_challenges(is_active=True)
challenge = challenges[0] if challenges else create_random_challenge()
user = User()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-timer', methods=['POST'])
def start_timer():
    tomato_timer.start()
    return jsonify({"status": "success", "message": "Timer started"})

@app.route('/api/stop-timer', methods=['POST'])
def stop_timer():
    tomato_timer.stop()
    return jsonify({"status": "success", "message": "Timer stopped"})

@app.route('/api/get-challenges', methods=['GET'])
def get_challenges():
    challenges = challenge.get_all_challenges()
    return jsonify(challenges)

@app.route('/api/get-user-info', methods=['GET'])
def get_user_info():
    user_info = user.get_user_info()
    return jsonify(user_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
