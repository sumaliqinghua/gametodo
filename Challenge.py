from datetime import datetime, timedelta
import json
import random
from random import randint
from statics import record_tomato_pertime, total_tomatoes_stats

from utilsd import datetime_decoder, datetime_handler


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
  def tojson(self):
    return {
        'name': self.name,
        'desc': self.desc,
        'bonus': self.bonus,
        'goal': self.goal,
        'cost': self.cost,
        'progress': self.progress,
        'start_time': self.start_time,
        'duration': self.duration,
        'failed': self.failed
    }
  def update_progress(self):
    self.progress += 1
    now = datetime.now()
    if now - datetime.fromisoformat(self.start_time) >= timedelta(hours=self.duration):
        # 已超时 //【?】超时但还未完成呢
        self.failed = True
    else:  
        self.progress += 1
    
  def is_completed(self):
    return self.progress >= self.goal
  
def create_challenge():
    # accept = input("是否接受挑战?(y/n)")
    # if accept == 'n':
    #     return
    data = {}
    data['name'] = input("输入挑战名称: ")
    data['desc'] = input("输入挑战描述: ")
    # data['bonus'] = float(input("完成任务后的奖励: "))
    data['goal'] = int(input("目标完成多少个番茄: "))
    data['cost'] = float(input("缴纳赌注: "))#float(data['goal'] * 20)
    data['progress'] = 0
    data['start_time'] = datetime.now().isoformat()
    data['duration'] = float(input("输入挑战时长(小时) "))
    data['failed'] = False
    #计算奖励
    calculate_bouns(data)

    return Challenge.load_from_dict(data)

def calculate_bouns(data):
    average_tomatoe_hour = record_tomato_pertime()/60#每个番茄耗时
    rand = random.uniform(1.2, 3.6)
    coeff = (data['goal'] * average_tomatoe_hour)/data['duration'] * rand
    data['bonus'] = data['cost'] * coeff
    print(f"当前平均番茄用时{average_tomatoe_hour} 预期用时{data['duration']} 奖励为: {data['bonus']}")

def create_random_challenge():
    total_tomatoes_stat = total_tomatoes_stats()
    data = {}
    data['name'] = "勇士的试炼"
    data['desc'] = "A randomly generated challenge."
    data['bonus'] = 0
    data['goal'] = randint(1, int(total_tomatoes_stat))
    data['cost'] = float(data['goal'] * 20)
    data['progress'] = 0
    data['start_time'] = datetime.now().isoformat()
    rand = random.uniform(0.4, 1)
    average_tomatoe_hour = record_tomato_pertime()/60#每个番茄耗时
    data['duration'] = average_tomatoe_hour * rand * data['goal']
    calculate_bouns(data)
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

    with open('json/challenges.json', 'r',encoding='utf-8') as f:
        data = json.load(f)
        # if 'start_time' in data:
        #     data['start_time'] = datetime.fromisoformat(data['start_time'])
        for c in data['active'] if is_active else data['finished']:
            challenges.append(Challenge.load_from_dict(c))
    # except:
    #     pass
    return challenges
# 传入的是激活的任务
def check_challenges(challenges, user):
    completed = [c.tojson() for c in challenges if c.is_completed()]
    for c in completed:
        if c['failed']:
            print("挑战已超时,无任何奖励")
            user.coins -= c['cost']
        else:
            print("挑战完成! 获得奖励"+str(c['bonus']))
            user.coins += c['bonus']
            user.gains += c['bonus']
    completed_before = load_challenges(False)
    completed_before.extend(completed) #这儿是列表类
    active = [c.tojson() for c in challenges if not c.is_completed()]
    completed_json = [c.tojson() for c in completed_before]
    data = {'active': active, 'finished': completed_json}
    with open('json/challenges.json', 'w',encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# def save_challenges():
#     completed = []

#     for c in challenges:
#         if c.is_completed():
#             completed.append(c.__dict__)

#     challenges = [c for c in challenges if not c.is_completed()]#未完成的

#     with open('challenges.json', 'w') as f:
#         json.dump({'active': [c.__dict__ for c in challenges],
#                     'finished': completed}, f)