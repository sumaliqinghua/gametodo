import os
 
import json
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("OPENAI_API_BASE")
api_key = os.getenv("OPENAI_API_KEY")

def load_raiseconversation(question):
    msg = [{"role": "system", 
                "content": "As an AI-powered praise robot, my purpose is to uplift and motivate you. Share your recent achievements with me, and I will provide heartfelt compliments, insightful encouragement, and confidence-boosting messages. Together, we will celebrate your current efforts, reinforce your determination, and inspire you to continue working hard. Answer in Chinese."
}]
    msg.append({"role": "user", "content": question})
    return msg

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

# a = load_raiseconversation()
# a = get_response(a)["choices"][0]["message"]
# print(a)