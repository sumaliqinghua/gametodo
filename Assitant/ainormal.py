import os
 
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat
load_dotenv()

#openai 1.0.0版本之后都推荐使用client方式访问api
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
#国内访问openai域名必须要走代理，这个是现成的一个反向代理
# client.base_url = os.getenv("OPENAI_API_BASE")
client.base_url = 'https://api.openai-proxy.com/v1'


def load_raiseconversation(question):
    msg = [{"role": "system", 
                "content": "As an AI-powered praise robot, my purpose is to uplift and motivate you. Share your recent achievements with me, and I will provide heartfelt compliments, insightful encouragement, and confidence-boosting messages. Together, we will celebrate your current efforts, reinforce your determination, and inspire you to continue working hard. Answer in Chinese."
}]
    msg.append({"role": "user", "content": question})
    return msg

# Send a request to the API and get a response
def get_response(msg,isJson = False):
    if isJson:
        response_format = ResponseFormat(type="json_object")
    else:
        response_format = ResponseFormat(type="text")
    try:
        completions = client.chat.completions.create(
        model='gpt-3.5-turbo',
        max_tokens=4096,
        n=1,
        stop=None,
        temperature=0.0,
        messages=msg,
        response_format= response_format
        )
        message = completions.choices[0].message.content
        return message
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

# a = load_raiseconversation("你好")
# a = get_response(a)
# print(a)