# # 用户数据
import json
import logging
import os
from datetime import datetime
from utilsd import savejson

logger = logging.getLogger(__name__)

# 定义User类
class User:
    def __init__(self):
        try:
            # 确保json目录存在
            if not os.path.exists('json'):
                os.makedirs('json')
                logger.info('Created json directory')
            
            if os.path.exists('json/user.json'):
                with open('json/user.json', encoding='utf-8') as f:
                    user_dict = json.load(f)
                
                # 使用get方法安全地获取值，提供默认值
                self.difficulty = user_dict.get('difficulty', '中等')
                self.task = user_dict.get('task', '工作')
                self.achievement = user_dict.get('achievement', 0.0)
                self.focus = user_dict.get('focus', 2)
                self.tomatoes = user_dict.get('tomatoes', 0)
                self.tomatoes_today = user_dict.get('tomatoes_today', 0)
                self.continuous = user_dict.get('continuous', 0)
                self.coins = user_dict.get('coins', 0.0)
                self.gains = user_dict.get('gain', 0.0)
                self.last_active_days = user_dict.get('last_active_days', datetime.now().date().isoformat())
                self.last_time = user_dict.get('last_time', "")
                
                logger.info('Successfully loaded user data from json/user.json')
            else:
                logger.warning('user.json not found, initializing with default values')
                self._init_default_values()
            
            # 检查是否需要重置每日数据
            self.check_and_reset_daily_data()
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding user.json: {str(e)}")
            self._init_default_values()
        except Exception as e:
            logger.error(f"Error initializing user: {str(e)}")
            self._init_default_values()
    
    def _init_default_values(self):
        """初始化默认值"""
        self.difficulty = '中等'
        self.task = '工作'
        self.achievement = 0.0
        self.focus = 2
        self.tomatoes = 0
        self.tomatoes_today = 0
        self.continuous = 0
        self.coins = 0.0
        self.gains = 0.0
        self.last_active_days = datetime.now().date().isoformat()
        self.last_time = ""
        # 保存默认值
        self.save_user_data()
        logger.info('Initialized user with default values')
    
    def check_and_reset_daily_data(self):
        """检查并重置每日数据"""
        try:
            if not hasattr(self, 'last_active_days') or not self.last_active_days:
                logger.warning('last_active_days not set, initializing to current date')
                self.last_active_days = datetime.now().date().isoformat()
                self.save_user_data()
                return

            current_date = datetime.now().date()
            last_active = datetime.fromisoformat(self.last_active_days).date()
            
            if current_date > last_active:
                logger.info(f'Resetting daily data. Current date: {current_date}, Last active: {last_active}')
                # 重置每日数据
                self.tomatoes_today = 0
                self.continuous = 0
                self.gains = 0
                self.last_active_days = current_date.isoformat()
                self.save_user_data()
                logger.info("Daily data reset successfully")
            else:
                logger.debug(f'No need to reset daily data. Current date: {current_date}, Last active: {last_active}')
                
        except ValueError as e:
            logger.error(f"Error parsing date: {str(e)}")
            # 重置为当前日期
            self.last_active_days = datetime.now().date().isoformat()
            self.save_user_data()
        except Exception as e:
            logger.error(f"Error checking daily data: {str(e)}")
            # 确保数据一致性
            self._init_default_values()
    
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
        # 确保在获取用户信息时检查日期
        self.check_and_reset_daily_data()
        return self.user_data_to_json()

    def gain_coins(self, coins):
        self.coins += coins
        self.save_user_data()

    def add_tomato(self):
        self.tomatoes += 1
        self.tomatoes_today += 1
        self.save_user_data()