import os
 
import json
import requests
from dotenv import load_dotenv

# completion = openai.ChatCompletion.create(
#                 # max_tokens = inf # 默认inf 最大令牌数
#                 presence_penalty = 1, # 惩罚机制，-2.0 到 2.0之间，默认0，数值越小提交的重复令牌数越多，从而能更清楚文本意思
#                 frequency_penalty = 1, # 意义和值基本同上，默认0，主要为频率
#                 temperature = 1.0,  # 温度 0-2之间，默认1  调整回复的精确度使用
#                 n = 1,  # 默认条数1
#                 user = 0,    # 用户ID，用于机器人区分不同用户避免多用户时出现混淆
#                 model = "gpt-3.5-turbo",    # 这里注意openai官方有很多个模型
#                 messages = msg
#             )
# 加载.env文件中的环境变量
load_dotenv()

# url = "https://openai.1rmb.tk/v1/chat/completions"
url = os.getenv("OPENAI_API_BASE")
api_key = os.getenv("OPENAI_API_KEY")

# Load the conversation history from a file
def load_conversation():
    try:
        with open("conversation.json", "r") as f:
            msg = json.load(f)
    except FileNotFoundError:
        msg = [{"role": "system", 
                "content": "You are a helpful assistant. Your response should be in JSON format."}]
    return msg

# Save the conversation history to a file
def save_conversation(msg):
    with open("conversation.json", "w", encoding='utf-8') as output:
        json.dump(msg, output, indent=4, ensure_ascii=False)

# Send a request to the API and get a response
def get_response(msg):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "gpt-3.5-turbo-1106",
        "messages": msg,
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

# Add a message to the conversation history and send a request
def add_message(msg, content):
    msg.append({"role": "user", "content": content})
    # Truncate the conversation history if it's too long
    if len(json.dumps(msg)) > 2048:
        msgtmp = msg[-5:]
    else:
        msgtmp = msg
    response = get_response(msgtmp)
    if response is not None:
        msg.append(response["choices"][0]["message"])
    else:#获取消息失败
        msg = msg[:-1]
    return msg

# Start the conversation
msg = load_conversation()
content = input("输入新内容: ")
msg = add_message(msg, content)
save_conversation(msg)
print("AI: " + msg[-1]["content"])