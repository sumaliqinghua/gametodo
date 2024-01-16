# # 用户数据
import json

from utilsd import savejson


# user = {
#   'difficulty': '中等',
#   'task': '工作',
#   'achievement': 0.0,
#   'focus': 2,
#   'tomatoes': 0,#总番茄数
#   'tomatoes_today': 0, #今日番茄数
#   'continuous': 0, #【?】//S:连续完成番茄数
#   'coins': 0.0,
#   'gain': 0.0,
#   'last_active_days': "",  #//S:连续使用天数//【C】保存上一次开始的时间，如果某次_time超过了24则把
#   'last_time': ''
# }
# 定义User类
class User:
    def __init__(self, difficulty, task, achievement, focus, tomatoes, tomatoes_today, continuous, coins, gain, last_active_days, last_time):
        self.difficulty = difficulty
        self.task = task
        self.achievement = achievement
        self.focus = focus
        self.tomatoes = tomatoes
        self.tomatoes_today = tomatoes_today
        self.continuous = continuous
        self.coins = coins
        self.gain = gain
        self.last_active_days = last_active_days
        self.last_time = last_time
    
    def user_data_to_json(self):
        user_data = {
            'difficulty': self.difficulty,
            'task': self.task,
            'achievement': self.achievement,
            'focus': self.focus,
            'tomatoes': self.tomatoes,
            'tomatoes_today': self.tomatoes_today,
            'continuous': self.continuous,
            'coins': self.coins,
            'gain': self.gain,
            'last_active_days': self.last_active_days,
            'last_time': self.last_time
        }
        return user_data
    def save_user_data(self):
        user_dict = self.user_data_to_json()
        savejson('json/user.json', user_dict)
        return user_dict

    def __init__(self):
        try:
            with open('json/user.json',encoding='utf-8') as f:
                user_dict = json.load(f)
            
            self.difficulty = user_dict['difficulty'] 
            self.task = user_dict['task']
            self.achievement = user_dict['achievement']
            self.focus = user_dict['focus']
            self.tomatoes = user_dict['tomatoes']
            self.tomatoes_today = user_dict['tomatoes_today']
            self.continuous = user_dict['continuous']
            self.coins = user_dict['coins']
            self.gain = user_dict['gain']
            self.last_active_days = user_dict['last_active_days']
            self.last_time = user_dict['last_time']
        
        except FileNotFoundError:
            print('user.json not found')

    def gain_coins(self, coins):
        self.coins += coins

    def add_tomato(self):
        self.tomatoes += 1