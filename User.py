# # 用户数据
import json
import logging
from utilsd import savejson

logger = logging.getLogger(__name__)

# 定义User类
class User:
    def __init__(self):
        try:
            with open('json/user.json', encoding='utf-8') as f:
                user_dict = json.load(f)
            
            self.difficulty = user_dict['difficulty'] 
            self.task = user_dict['task']
            self.achievement = user_dict['achievement']
            self.focus = user_dict['focus']
            self.tomatoes = user_dict['tomatoes']
            self.tomatoes_today = user_dict['tomatoes_today']
            self.continuous = user_dict['continuous']
            self.coins = user_dict['coins']
            self.gains = user_dict['gain']
            self.last_active_days = user_dict['last_active_days']
            self.last_time = user_dict['last_time']
        
        except FileNotFoundError:
            logger.warning('user.json not found, initializing with default values')
            self.difficulty = '中等'
            self.task = '工作'
            self.achievement = 0.0
            self.focus = 2
            self.tomatoes = 0
            self.tomatoes_today = 0
            self.continuous = 0
            self.coins = 0.0
            self.gains = 0.0
            self.last_active_days = ""
            self.last_time = ""
            # Save the default values
            self.save_user_data()
        except Exception as e:
            logger.error(f"Error initializing user: {str(e)}")
            raise
    
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
            'gain': self.gains,
            'last_active_days': self.last_active_days,
            'last_time': self.last_time
        }
        return user_data

    def save_user_data(self):
        user_dict = self.user_data_to_json()
        savejson('json/user.json', user_dict)
        return user_dict

    def get_user_info(self):
        return self.user_data_to_json()

    def gain_coins(self, coins):
        self.coins += coins
        self.save_user_data()

    def add_tomato(self):
        self.tomatoes += 1
        self.tomatoes_today += 1
        self.save_user_data()