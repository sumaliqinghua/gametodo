from datetime import datetime
import json
import os

from utilsd import savejson
from User import User
file_path = 'json/tomatoesAll.json'

#返回的是列表，每一天的
def daily_stats(data):
    results = {}
    for date, users in data.items():
        gains = [user['gain'] for user in users]
        results[date] = {
            'total': sum(gains),
            'average': sum(gains) / len(gains) 
        }

    return results

# 这个算的是当日一个番茄平均挣多少钱
# '2023-01-01'
def daily_stats(date):
  data = get_all_tomatoes_data()
  try:
    users = data[date]
  except KeyError:
    return {
      'total': 0,
      'average': 0
    }
  
  gains = [user['gain'] for user in users]

  return {
      'total': sum(gains),
      'average': sum(gains) / len(gains)
  }

def total_stats():
    data = get_all_tomatoes_data()
    total_gains = 0
    num_users = 0
    num_days = 0
    for users in data.values():
        gains = [user['gain'] for user in users]
        total_gains += sum(gains)
        num_users += len(gains)
        num_days += 1

    return {
        'total': total_gains,#总收入
        'daily_average_gains': round(total_gains/num_days,2),
        'average': round(total_gains / num_users,2)#平均一个番茄挣多钱
    }

#计算番茄平均数
def total_tomatoes_stats(includeLastDay = False):
    data = get_all_tomatoes_data()
    total_users = 0
    
    total_users = 0
    num_days = 0
    today = datetime.today().strftime('%Y-%m-%d')
    for date,users in data.items():
        if not includeLastDay and date == today:
            continue
        total_users += len(users)
        num_days += 1
  
    return total_users / num_days

# 总番茄统计
def record_all_tomatoes(user):
    data = get_all_tomatoes_data()

    # 获取当前日期
    today = datetime.today().strftime('%Y-%m-%d')
    user = user.user_data_to_json()
    # 检查当前日期是否已在字典中 会立马写入，不要纯调用这个
    if today in data:
        data[today].append(user)
    else:
        data[today] = [user]
    savejson(file_path,data)
    show_today_stats()

# 每个番茄的平均用时
def record_tomato_pertime():
    data = get_all_tomatoes_data()
    average_time = 0
    for users in data.values():
        #最后一个减去第一个
        if len(users) <= 1:
            continue
        mins = calculate_mins(users[0]['last_time'],users[-1]['last_time'])
        average_time_tmp = mins/(len(users)-1)
        average_time += average_time_tmp
    average_time /= len(data)
    return average_time

def calculate_mins(first, last):
    return (datetime.fromisoformat(last) - datetime.fromisoformat(first)).total_seconds() / 60

def get_all_tomatoes_data():
    file_exists = os.path.exists(file_path)
    if file_exists:
        with open(file_path, 'r',encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = {}
    return data

def show_today_stats():
    today = datetime.today().strftime('%Y-%m-%d')
    print('今日收入情况 {}'.format(daily_stats(today)))