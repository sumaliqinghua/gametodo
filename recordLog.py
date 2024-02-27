from datetime import datetime
from random import randint

from Assitant.ainormal import get_response, load_raiseconversation


def add_record():

  current_time = datetime.now()  
  record = f"{current_time.year}年{current_time.month}月{current_time.day}日{current_time.hour}:{current_time.minute}:{current_time.second}\n"
  
  questions = ["1. 实际进度: ", "2. 困难/浪费: ", "3. 学到/收获: ", "4. 做得好的/不好的: ", "5. 改进措施: ", "6. 后续: ", "7. 鼓励: ", "8. 自我评分: "]
  
  for question in questions:
    answer = input(question)
    if answer == 's':
      # 如果输入s,则跳出循环
      record += f"{question}\n"
      break
    record += f"{question}{answer}\n"

  # 将剩余问题的答案设为空
  for question in questions[questions.index(question)+1:]:
    record += f"{question}\n"
  judegment = judge_record(record)
  print(judegment)
  record += f"9. AI点评: {judegment}\n"

  with open("recordLog.txt", "r+",encoding='utf-8') as f:
    content = f.read()
    f.seek(0, 0)
    f.write(record + "\n" + content)
  print("\n记录已保存，粘贴到笔记中并【开启休息计时】吧!\n")
  index = randint(1,9)
  play_audio(f"./Assets/wav/{index}.wav")
def judge_record(content):
  content = load_raiseconversation(content)
  try:
    judgment = get_response(content)
  except:
    judgment = "AI出错了，请重试"
  return judgment


import os

def play_audio(filename):
    # index = randint(1,9)
    # 使用afplay命令播放音频
    os.system(f'afplay {filename}')
# play_audio(f"./Assets/wav/{index}.wav")