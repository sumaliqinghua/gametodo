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
        with open("json/conversation.json", "r", encoding='utf-8') as f:
            msg = json.load(f)
    except FileNotFoundError:
        msg = [{"role": "system", 
                "content": '''
Let's play a game, you are going to act as AdventureGPT an AI capable of generating and manage an adventure text based game based on a title chosen by me.
The game works like this: based on the title and the information I choose, you will generate a text game. Always keep in mind what happens in the game, for example if the player has lost health in battle, keep count! make sure that the game has all the necessary dynamics to entertain and excite the player, for example add information and secondary missions. Also, when a new scene based on a player's choice is loaded, always add lore of information regarding the fictional world in which the story is set, connected to the events being told.
And make that output text in structured JSON format exactly like this:
{
    "Title": "",
    "Turns": 1,
    "Health": {
        "current": 100,
        "maximum": 100
    },
    "Goal": "",
    "Scene": "",
    "Dialogue": "",
    "PossibleActions": {
        "1": "",
        "2": "",
        "3": "",
        "4": ""
    }
}
Before generating a complete plot, the current turns need to be determined. When the turn number is a multiple of 5, a conflict or contradiction arises in the plot to increase the story's interest, and when the turn number is a multiple of 11, a new scene is entered. You must remember the rules of turns!
And here is an explanation of each field in the JSON:
"Turns:"<starting from 1, it increases only by one with each answer">
"Health: " <the health of the character n/100>,
"Goal: " <the closest goal in order to advance in the story, Once you determine that the player has completed this objective, you must switch to the next objective to drive the plot forward. It's important!>,
"Scene: " <a detailed reconstruction of the scene, the first three lines are about the description of the place, then what is happening inside the place is also explained. Also explain what the character does, if he finds any objects, if he sees something in particular, describe everything>,
"Dialogue: " <the dialogue recreates sounds, whispers, words, people talking, ambient noises, literally showing the onomatopoeias of sounds, do never explain what the character is hearing, just write it as a sound or a dialogue>,
"PossibleActions: " <a numbered list of 4 possible actions to advance the story, with increasing difficulty from the first to the last one.The first one is a beneficial option, the last one is a bad and harmful option may cause a decrease in health."
'''}]
    return msg

# Save the conversation history to a file
def save_conversation(msg):
    with open("json/conversation.json", "w", encoding='utf-8') as output:
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
        "response_format":{"type": "json_object"}
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
        msgtmp = [msg[0]] + msg[-2:]
    else:
        msgtmp = msg
    response = get_response(msgtmp)
    if response is not None:
        msg.append(response["choices"][0]["message"])
    else:#获取消息失败
        msg = msg[:-1]
    return msg

# Start the conversation
def start_conversation(input):
    if input>20 and input % 5 ==0:
        input = "change the content of 'Goal'"
    elif input>20 and input % 3 ==0:
        input = "'Health' increase"
    elif input>20 and input % 4 ==0:
        input = '1'
    elif input>20 and input % 6 ==0:
        input = 'Use props to change the course of the story'
    else:
        input = input % 4 + 1
    msg = load_conversation()
    content = str(input)
    print("你选择了"+content)
    msg = add_message(msg, content)
    save_conversation(msg)
    print("AI: " + msg[-1]["content"])# //【?】好像不是打印的最后一条
# start_conversation(2-1)