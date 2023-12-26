from datetime import datetime, timedelta
import json
import random
from random import randint
from statics import total_tomatoes_stats

from utils import datetime_decoder, datetime_handler


class Challenge():
  def __init__(self, data):
    self.name = data['name']
    self.desc = data['desc']
    self.bonus = data['bonus']
    self.goal = data['goal']
    self.cost = data['cost']
    self.progress = data['progress']
    self.start_time = data['start_time']  
    self.duration = data['duration'] # 持续时间,单位:小时
    self.failed = data['failed']

  @classmethod
  def load_from_dict(cls, data):
    return cls(data)
  
  def update_progress(self):
    self.progress += 1
    now = datetime.now()
    if now - self.start_time >= timedelta(hours=self.duration):
        # 已超时
        self.failed = True
    else:  
        self.progress += 1
    
  def is_completed(self):
    return self.progress >= self.goal
  
# class Challenges():
  
#   def __init__(self):
#     self.active = []
#     self.finished = []
  
#   def add(self, challenge):
#     self.active.append(challenge)
  
#   def complete(self, challenge):
#     self.active.remove(challenge)
#     self.finished.append(challenge)

def create_challenge():
    accept = input("是否接受挑战?(y/n)")
    if accept == 'n':
        return
    data = {}
    data['name'] = input("输入挑战名称: ")
    data['desc'] = input("输入挑战描述: ")
    data['bonus'] = float(input("Enter the bonus for completing the challenge (in dollars): "))
    data['goal'] = int(input("完成多少个番茄: "))
    data['cost'] = float(data['goal'] * 10)
    data['progress'] = 0
    data['start_time'] = datetime.now()
    data['duration'] = float(input("输入挑战时长(小时) "))
    data['failed'] = False
    #计算奖励
    average_tomatoe_hour = total_tomatoes_stats() / 24
    coeff = (data['goal'] / average_tomatoe_hour)/data['duration']
    data['bonus'] = data['cost'] * coeff
    return Challenge.load_from_dict(data)

def create_random_challenge():
    total_tomatoes_stat = total_tomatoes_stats()
    data = {}
    data['name'] = "Random Challenge"
    data['desc'] = "A randomly generated challenge."
    data['bonus'] = 0
    data['goal'] = randint(1, int(total_tomatoes_stat * 3))
    data['cost'] = float(data['goal'] * 10)
    data['progress'] = 0
    data['start_time'] = datetime.now()
    data['duration'] = random.uniform(12, 100)
    average_tomatoe_hour = total_tomatoes_stat / 24
    coeff = (data['goal'] / average_tomatoe_hour) / data['duration']
    data['bonus'] = data['cost'] * coeff
    data['failed'] = False
    print("A random challenge has been created."
            "\nChallenge Name:", data['name'],
            "\nChallenge Description:", data['desc'],
            "\nChallenge Goal:", data['goal'],
            "\nChallenge Cost:", data['cost'],
            "\nChallenge Bonus:", data['bonus'],
            "\nChallenge Duration:", data['duration'])
    accept = input("是否接受挑战?(y/n)")
    if accept == 'n':
        return
    else:
        return Challenge.load_from_dict(data)

def load_challenges(is_active):
    challenges = []
    try:
        with open('challenges.json', 'r',encoding='utf-8') as f:
            data = json.load(f, object_hook=datetime_decoder)
            for c in data['active'] if is_active else data['finished']:
                challenges.append(Challenge.load_from_dict(c))
    except:
        pass
    return challenges
# 传入的是激活的任务
def save_challenges(challenges, user):
    completed = [c.__dict__ for c in challenges if c.is_completed()]
    for c in completed:
        if c.failed:
            print("挑战已超时,无任何奖励")
        else:
            print("挑战完成!")  
            user.coins += c['bonus']
            user.gains += c['bonus']
    completed_before = load_challenges(False)
    completed_before.extend(completed)
    active = [c.__dict__ for c in challenges if not c.is_completed()]
    data = {'active': active, 'finished': completed}
    with open('challenges.json', 'w',encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=datetime_handler)

# def save_challenges():
#     completed = []

#     for c in challenges:
#         if c.is_completed():
#             completed.append(c.__dict__)

#     challenges = [c for c in challenges if not c.is_completed()]#未完成的

#     with open('challenges.json', 'w') as f:
#         json.dump({'active': [c.__dict__ for c in challenges],
#                     'finished': completed}, f)