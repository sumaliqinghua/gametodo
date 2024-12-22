from datetime import datetime, timedelta
import json
import random
import logging
from random import randint
from statics import record_tomato_pertime, total_tomatoes_stats
from utilsd import datetime_decoder, datetime_handler

logger = logging.getLogger(__name__)

class Challenge():
    def __init__(self, data):
        self.name = data['name']
        self.desc = data['desc']
        self.bonus = data['bonus']
        self.goal = data['goal']
        self.cost = data['cost']
        self.progress = data['progress']
        self.start_time = data['start_time']  
        self.duration = data['duration'] # 持续时间,单位:分钟
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

    def get_all_challenges(self):
        try:
            with open('json/challenges.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'active': [Challenge.load_from_dict(c).tojson() for c in data.get('active', [])],
                    'finished': [Challenge.load_from_dict(c).tojson() for c in data.get('finished', [])]
                }
        except FileNotFoundError:
            logger.warning("challenges.json not found, initializing with empty lists")
            return {'active': [], 'finished': []}
        except Exception as e:
            logger.error(f"Error loading challenges: {str(e)}")
            raise

    def update_progress(self):
        try:
            now = datetime.now()
            start_time = datetime.fromisoformat(self.start_time)
            dvalue = now - start_time
            
            if dvalue <= timedelta(hours=0):
                return
            elif dvalue >= timedelta(hours=self.duration/60):
                self.failed = True
                logger.info("Challenge failed: exceeded time limit by {} minutes".format(
                    dvalue.total_seconds()/60 - self.duration))
            else:  
                self.progress += 1
                logger.info("Challenge progress: {}/{} for '{}'".format(
                    self.progress, self.goal, self.name))
                delay = dvalue.total_seconds()/60 - (30 * (self.progress - 1) + 25)
                logger.debug(f"Current delay: {delay}min, Flexible time remaining: {self.duration - self.goal * 30 - delay}min")
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}")
            raise

    def is_completed(self):
        return self.progress >= self.goal

def create_challenge():
    try:
        data = {}
        data['name'] = input("输入挑战名称: ")
        print("输入挑战描述: ")
        lines = []
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                break
        data['desc'] = lines
        data['goal'] = int(input("目标完成多少个番茄: "))
        data['cost'] = float(input("缴纳赌注: "))#float(data['goal'] * 20)
        data['progress'] = 0
        data['start_time'] = input_time().isoformat()
        data['duration'] = float(input("输入挑战时长(分钟) "))
        data['failed'] = False
        calculate_bouns(data)
        return Challenge(data)
    except Exception as e:
        logger.error(f"Error creating challenge: {str(e)}")
        raise

def input_time():
    try:
        user_input = input("请输入开始时间（HH.MM，例如 15.30）,留空则立马开始：")
        time_format = "%H.%M"
        user_time = datetime.strptime(user_input, time_format).time()
        current_date = datetime.now().date()
        datetime_combined = datetime.combine(current_date, user_time)
        print("结合当前日期的 datetime 对象为：", datetime_combined)
        return datetime_combined
    except ValueError:
        return datetime.now()

def calculate_bouns(data):
    try:
        average_tomatoe_hour = record_tomato_pertime()/60#每个番茄耗时
        rand = random.uniform(1.2, 2.2)
        coeff = (data['goal'] * average_tomatoe_hour * 60)/data['duration'] * rand
        data['bonus'] = data['cost'] * coeff
        print(f"标准用时{average_tomatoe_hour * data['goal']} 预期用时{data['duration']/60} 奖励为: {data['bonus']}")
    except Exception as e:
        logger.error(f"Error calculating bonus: {str(e)}")
        raise

def create_random_challenge():
    """创建随机挑战"""
    try:
        # 生成随机挑战参数
        goal = random.randint(1, 3)
        duration = random.uniform(24, 72)  # 1-3天
        cost = 20.0
        bonus = cost * random.uniform(1.5, 3.0)
        
        print(f"预计时{duration} 实际时{duration * 0.625} 倍为: {bonus}")
        
        # 创建挑战对象
        challenge = Challenge(
            name="随机挑战",
            desc=["开始一个随机挑战！"],
            goal=goal,
            cost=cost,
            bonus=bonus,
            duration=duration
        )
        
        return challenge
    except Exception as e:
        logger.error(f"Error creating random challenge: {str(e)}")
        return None

def load_challenges(is_active):
    try:
        challenges = []
        with open('json/challenges.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for c in data['active'] if is_active else data['finished']:
                challenges.append(Challenge.load_from_dict(c))
        return challenges
    except FileNotFoundError:
        logger.warning("challenges.json not found")
        return []
    except Exception as e:
        logger.error(f"Error loading challenges: {str(e)}")
        raise

def check_challenges(challenges, user):
    try:
        completed = [c for c in challenges if c.is_completed() or c.failed]
        for c in completed:
            if c.failed:
                dvalue = datetime.now() - datetime.fromisoformat(c.start_time)
                if dvalue <= timedelta(minutes=20+c.duration):
                    print("挑战已超时,但未超过20min有奖励{}".format(c.cost/3))
                    user.coins += c.cost/10
                    user.gains += c.cost/10
                else:
                    print("挑战{} 已超时,无任何奖励".format(c.name))
            else:
                print("挑战{} 完成! 获得奖励".format(c.name)+str(c.bonus))
                user.coins += c.bonus
                user.gains += c.bonus
        completed_before = load_challenges(False)
        completed_before.extend(completed) #completed_before是列表类 而completed在上面转换过了
        active = [c.tojson() for c in challenges if not c.failed and not c.is_completed()]
        completed_before = [c.tojson() for c in completed_before]
        data = {'active': active, 'finished': completed_before}
        with open('json/challenges.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error checking challenges: {str(e)}")
        raise