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

# 难度系数
DIFFICULTY = {'简单': 1, '中等': 1.5, '困难': 1.8}
TASK_TYPE = {'工作': 1.2, '爱好': 1, '杂事': 0.7}
# 专注程度
FOCUS_LEVEL = {0:0.6, 1:0.8, 2:1.0, 3:1.2, 4:1.5}
#超时程度
Time_LEVEL = {0:0.6, 1:0.8, 2:1.0, 3:1.2, 4:1.5}
# 每日目标和奖励
# 检测到今日首次登陆时设置今日目标
# //【C】今日到指定个数番茄额外奖励
# 保留小数两位
DAILY_GOAL = 8
DAILY_REWARD = 50

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
                coins = calculate_coins("番茄时间", 1, time_delta)
                self.user.add_coins(coins)
                record_tomatoes()
            self.start_time = None
            return True
        return False

def calculate_coins(task, continuous_count,time_delta):
    
    # 计算难度和任务类型系数
    difficulty_coeff = DIFFICULTY[user.difficulty]
    task_coeff = TASK_TYPE[task]
    
    if continuous_count < 6:
        # 连击奖励系数,连击数每增加1,奖励系数增长20%
        continuous_coeff = 1 + 0.2 * continuous_count  
    else:
        continuous_coeff = 2 + 0.1 * (continuous_count - 5)  
    print("连击系数{}".format(continuous_coeff))

    # 计算单个番茄钟的奖励
    reward = BASE_REWARD * difficulty_coeff * task_coeff * continuous_coeff
    time_delta -= 25
    if time_delta <= 0:
        time_punish = 0
    # elif time_delta > 120:
    #     time_punish = 10
    else:
        time_punish = 1.5 * math.log(time_delta+1)
    print('时间耗费{}'.format(time_punish))
    reward -= time_punish
    # 成果分直接累加到奖励中
    reward += user.achievement * reward
    # 根据专注度得到系数乘以基础奖励
    focus_coeff = FOCUS_LEVEL[user.focus]
    reward = reward * focus_coeff
    reward = round(reward, 2)
    if firstLaunch:
        return reward
    #   # 加上连续奖励  
    #   if is_continuous:
    #     continuous_bonus = CONTINUOUS_BONUS * (tomatoes // 4)
    #     reward += continuous_bonus
    
    # 加上时间因素奖励 特定任务奖励
    # if user.task == 'urgent':
    #     reward *= URGENT_BONUS
    #特定时间奖励
    #   if datetime.date.today().day == 1:  //S:限时赛事奖励
    #     reward *= LIMIT_BONUS
    last_time = datetime.fromisoformat(user.last_time)
    # 添加随机奖励
    if last_time:
        delta = (datetime.now() - last_time).total_seconds() / 3600
        if random.random() < 1 - delta:
            random_bonus = random.uniform(0.5, 0.6 * BASE_REWARD * (1+continuous_coeff))
            print("太棒了，掉落随机奖励{}".format(random_bonus))
            reward += random_bonus
    reward = round(reward, 2)
    return reward
  
def main():
    global user,firstLaunch
    # 加载用户数据
    print('当前时间{}, 欢迎━(*｀∀´*)ノ亻!'.format(datetime.now().isoformat()))
    user = User()
    operation = input("请选择服务(番茄记录1/进入商城2/纯日志记录3/录入挑战任务4):")
    if not operation or operation == "1":
        record_tomatoes()
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

def record_tomatoes():
    # 输入当前数据
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
    continuous_count = 0
    time_delta = 0
    if firstLaunch:
        print("欢迎您使用未来科技提升系统👏🏻，在游戏中改进您的真实属性")
    else:
        # 计算时间间隔
        last_time = datetime.fromisoformat(user.last_time)
        time_delta = (datetime.now() - last_time).total_seconds() / 60
        print("系统正在加强您的属性👏🏻改变正在发生，距离上次提升记录已过去{}分钟".format(time_delta))
        is_continuous = time_delta <= 25+20#在20分钟内又完成了一个番茄
        if is_continuous:
            continuous_count = user.continuous + 1
    
    user.difficulty = difficulty
    user.task = task
    user.focus = focus
    user.achievement = achievement

    # 计算本次获得的金币数
    coins = calculate_coins(task, continuous_count, time_delta)
  
    # 处理衰减逻辑
    handle_decay()

    # 更新用户数据
    user.coins += coins
    user.gains = coins
    user.last_time = datetime.now().isoformat()
    user.time_delta = time_delta
    user.tomatoes += 1
    user.tomatoes_today += 1
    user.continuous = continuous_count
    
    if user.last_active_days == "":
        user.last_active_days = datetime.now().isoformat()
    
    # 检查是否达到每日目标
    if user.tomatoes_today == DAILY_GOAL:
        print('恭喜达到每日目标!获得额外奖励{}金币'.format(DAILY_REWARD))
        user.coins += DAILY_REWARD
        user.gains += DAILY_REWARD
        user.save_user_data()
        
    try:
        challenges = load_challenges(True)
    except:
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
        # challenges = generate_challenges(user)
        challenge = create_random_challenge()
        if challenge:
            challenges = [challenge]
            print("新挑战任务:{} ".format(challenge.name))
    check_challenges(challenges, user)
    record_all_tomatoes(user)
    print('本次获得 {} 金币'.format(coins))
    print('当前金币数:{}'.format(user.coins))
    # result = max(min(coins/5, 6), 1)
    # //【C】改为和任务系统结合
    # start_conversation(int(coins))

def handle_decay():
    try:
        last_time = datetime.strptime(user.last_time, "%Y-%m-%dT%H:%M:%S.%f")
    except:
        last_time = datetime.now()

    current_time = datetime.now()
    active_days = 0
    last_date = datetime.date(last_time)#上一次记录番茄的时间
    # last_date = datetime.date(last_time.year, last_time.month, last_time.day)#上一次记录番茄的时间
    current_date = datetime.date(current_time)
    days_diff = (current_date - last_date).days
    if(days_diff > 0):
        user.tomatoes_today = 0
    if(days_diff > 1):
        user.last_active_days = datetime.now().isoformat()
        print("连续日期记录已经中断")
    else:
        try:
            last_active_days = datetime.strptime(user.last_active_time, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            last_active_days = datetime.now()
        last_active_date = datetime.date(last_active_days)#连续记录开始的最早时间
        active_days = (current_date - last_active_date).days

    if user.coins > DECAY_AMOUNT:
        decay_rate = DECAY_RATE
        if active_days >= 3:
            decay_rate /= 2 
        delta_hours = (current_time - last_time).total_seconds() / 3600

        decayed = int(user.coins * decay_rate * delta_hours / 24)
        print('金币衰减了{}!'.format(decayed))
        user.coins -= decayed

if __name__ == '__main__':
    main()