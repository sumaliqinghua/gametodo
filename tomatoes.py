# import datetime.datetime as data
from datetime import datetime
import json
import math
import os
import random
from Assitant.airequest import start_conversation
from Challenge import create_challenge, create_random_challenge, load_challenges, check_challenges
from User import User

from product import CanBuyOne, GotoStore, PurchaseProduct, RecordProduct, show_products
from recordLog import add_record
from statics import record_all_tomatoes, show_today_stats
from utilsd import savejson

# 基础配置
BASE_REWARD = 7 # 每个番茄钟的基础奖励
# CONTINUOUS_BONUS = 40 # 连续完成4个番茄钟的额外奖励

# 常量定义
TASK_TYPE = {
    '工作': 1.2,
    '爱好': 1.0,
    '杂事': 0.8,
    '番茄时间': 1.0
}

DIFFICULTY = {
    '简单': 0.8,
    '中等': 1.0,
    '困难': 1.2
}

DAILY_GOAL = 8  # 每日目标番茄数
DAILY_REWARD = 5  # 达到每日目标的额外奖励

# 专注程度
FOCUS_LEVEL = {0:0.6, 1:0.8, 2:1.0, 3:1.2, 4:1.5}
#超时程度
Time_LEVEL = {0:0.6, 1:0.8, 2:1.0, 3:1.2, 4:1.5}
# 每日目标和奖励
# 检测到今日首次登陆时设置今日目标
# //【C】今日到指定个数番茄额外奖励
# 保留小数两位
DECAY_AMOUNT = 50 #达到此数值开始衰减
DECAY_RATE = 0.08


# 时间因素
URGENT_BONUS = 1.5 # 紧急任务加成
LIMIT_BONUS = 2 # 限时赛事加成

# 商品兑换
PRODUCTS = {'电池': 20, '帽子': 100, '奖杯': 200}

firstLaunch = False

class TomatoTimer:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.user = User()

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = datetime.now()
            return True
        return False

    def stop(self):
        if self.running:
            self.running = False
            end_time = datetime.now()
            time_delta = (end_time - self.start_time).total_seconds() / 60
            if time_delta >= 25:
                coins = calculate_coins(self.user, "番茄时间", 1, time_delta)
                self.user.add_coins(coins)
                record_tomatoes(self.user)
            self.start_time = None
            return True
        return False

def calculate_coins(user, task_type, continuous_count=0, time_delta=0):
    """计算获得的金币数
    Args:
        user (User): 用户对象
        task_type (str): 任务类型
        continuous_count (int): 连续完成的番茄数
        time_delta (float): 距离上次番茄的时间间隔(分钟)
    """
    # 基础奖励
    reward = 1.0
    
    # 任务类型加成
    task_coeff = TASK_TYPE.get(task_type, 1.0)
    reward *= task_coeff
    
    # 难度加成
    difficulty_coeff = DIFFICULTY[user.difficulty]
    reward *= difficulty_coeff
    
    # 连续完成加成
    continuous_coeff = min(continuous_count * 0.1 + 1, 2)
    reward *= continuous_coeff
    
    # 专注度加成
    focus_coeff = 1 + user.focus * 0.1
    reward *= focus_coeff
    
    # 成果加成
    achievement_coeff = 1 + user.achievement
    reward *= achievement_coeff
    
    # 时间衰减
    if time_delta > 60 * 3:  # 超过3小时
        decay = min((time_delta - 60 * 3) / (60 * 24), 0.5)  # 最多衰减50%
        reward *= (1 - decay)
    
    reward = round(reward, 2)
    return reward
  
def record_tomatoes(user, difficulty=None, task=None, focus=None, achievement=None):
    """记录番茄钟完成情况
    Args:
        user (User): 用户对象
        difficulty (str): 难度 ('简单'/'中等'/'困难')
        task (str): 任务类型 ('工作'/'爱好'/'杂事')
        focus (int): 专注度 (0-4)
        achievement (float): 成果分 (0-1)
    """
    continuous_count = 0
    time_delta = 0

    if firstLaunch:
        print("欢迎您使用未来科技提升系统👏🏻，在游戏中改进您的真实属性")
    else:
        # 计算时间间隔
        try:
            last_time = datetime.fromisoformat(user.last_time) if user.last_time else datetime.now()
            time_delta = (datetime.now() - last_time).total_seconds() / 60
            print("系统正在加强您的属性👏🏻改变正在发生，距离上次提升记录已过去{}分钟".format(time_delta))
            is_continuous = time_delta <= 25+20  # 在20分钟内又完成了一个番茄
            if is_continuous:
                continuous_count = user.continuous + 1
        except Exception as e:
            print(f"Error calculating time delta: {str(e)}")
            time_delta = 0
    
    # 更新用户数据
    user.difficulty = difficulty
    user.task = task
    user.focus = focus
    user.achievement = achievement

    # 计算本次获得的金币数
    coins = calculate_coins(user, task, continuous_count, time_delta)
  
    # 处理衰减逻辑
    handle_decay(user)

    # 更新用户数据
    user.coins += coins
    user.gains = coins
    user.last_time = datetime.now().isoformat()
    user.time_delta = time_delta
    user.tomatoes += 1
    user.tomatoes_today += 1
    user.continuous = continuous_count
    
    if not user.last_active_days:
        user.last_active_days = datetime.now().isoformat()
    
    # 检查是否达到每日目标
    if user.tomatoes_today == DAILY_GOAL:
        print('恭喜达到每日目标!获得额外奖励{}金币'.format(DAILY_REWARD))
        user.coins += DAILY_REWARD
        user.gains += DAILY_REWARD
    
    user.save_user_data()
        
    try:
        challenges = load_challenges(True)
    except Exception as e:
        print(f"Error loading challenges: {str(e)}")
        challenges = []

    if challenges and len(challenges) != 0:
        #更新challege的进度
        for challenge in challenges:
            challenge.update_progress()
            if challenge.failed:
                print("任务失败:{}".format(challenge.desc[-1]))
            else:
                print("任务描述:{}".format(challenge.desc[challenge.progress]))
    else:
        # 没有未完成挑战,按概率触发新的
        challenge = create_random_challenge()
        if challenge:
            challenges = [challenge]
            print("新挑战任务:{} ".format(challenge.name))
    
    check_challenges(challenges, user)
    record_all_tomatoes(user)
    print('本次获得 {} 金币'.format(coins))
    print('当前金币数:{}'.format(user.coins))
    
    return {
        'coins_earned': coins,
        'total_coins': user.coins,
        'continuous_count': continuous_count,
        'time_delta': time_delta
    }

def handle_decay(user):
    """处理金币衰减
    Args:
        user (User): 用户对象
    """
    try:
        if user.coins > DECAY_AMOUNT:
            decay = user.coins * DECAY_RATE
            user.coins = round(user.coins - decay, 2)
            print(f"金币衰减: -{decay:.2f}")
    except Exception as e:
        print(f"Error handling decay: {str(e)}")

def main():
    global user,firstLaunch
    # 加载用户数据
    print('当前时间{}, 欢迎━(*｀∀´*)ノ亻!'.format(datetime.now().isoformat()))
    user = User()
    operation = input("请选择服务(番茄记录1/进入商城2/纯日志记录3/录入挑战任务4):")
    if not operation or operation == "1":
        difficulty = input('请输入难度(简单1/中等2/困难3):')  #根据数字转成对应的中文
        task = input('请输入任务类型(工作1/爱好2/杂事3):')

        difficulty_dict = {
            '1': '简单',
            '2': '中等',
            '3': '困难',
        }

        task_dict = {
            '1': '工作',
            '2': '爱好',
            '3': '杂事',
        }

        difficulty = difficulty_dict[difficulty]
        task = task_dict[task]
        focus = int(input("请输入专注度 0:'不在状态', 1:'不佳', 2:'一般', 3:'比较投入', 4:'全神贯注':"))
        while True:
            achievement = float(input('请输入成果分(0-1):'))
            if 0 <= achievement <= 1:
                break
            else:
                print('成果分必须在0-1之间,请重新输入')
        record_tomatoes(user, difficulty, task, focus, achievement)
        show_products()
        dvalue,x = CanBuyOne(user.coins)
        print('当前现金购买商品{},{}{}元'.format(x, '多出' if dvalue > 0 else '还差',abs(round(dvalue,2))))
        record = input("是否立即记录日志(否0/是1):")
        if record == "1" or record == "":
            add_record()
        user.save_user_data()
    elif operation == "2":
        GotoStore(user)
    elif operation == "3":
        add_record()
    elif operation == "4":
        try:
            challenges = load_challenges(True)
        except:
            challenges = []
        # if challenges == None or len(challenges) == 0:
            
        challange = create_challenge()
        user.coins -= challange.cost
        challenges.append(challange)
        check_challenges(challenges,user)
        user.save_user_data()

    else:
        print("无效的选择")
        return

if __name__ == '__main__':
    main()