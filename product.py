#原价 折扣
#读取待售商品
#随机掉落限时折扣，如果在xx时间内完成下一个番茄商品降价
# # 用户数据
from datetime import datetime
import json
import os
import random
from statics import total_stats

from utils import savejson

product_file_path = 'product.json'
product_type_dict = {
        '1': '娱乐',
        '2': '服装',
        '3': '健康',
        '4': '出行',
        '5': '教育',
        '6': '数码',
        '7': '其他'
        # //【?】虚拟的单独一类？
    }
product = {
      "name": "厚帽子",
      "price": 15.0,
      "type": "其他",
      "discountCoefficient": 0.8,
      "discountDay": -1,#折扣日 日期个位正好和价格个位数相等 0.6-0.99折扣
      "firstRecordTime": "",#添加产品后首次记录番茄的时间
      "purchaseTime": ""
    }
def RecordProduct():
    name = input("请输入商品名称:")
    type = input("请选择商品分类: 娱乐1/服装2/健康3/出行4/教育5/数码6/其他7")
    type = product_type_dict[type]
    price = float(input("请输入商品价格:"))
    # 当价格超出一天平均日的gain时询问希望几天内获得，调整商品价格并确认
    average_gains = total_stats()['daily_average_gains']

    if price > average_gains * 1.5:
        adjust = input("该商品价格较高,是否调整商品价格?(y/n)")
        if adjust == 'y':
            days = int(input("您希望在几天内获得该商品?"))
            new_price = average_gains * days
            confirm = input(f"该商品价格调整为{new_price},确定使用新价格吗?(y/n)")
            if confirm == 'y':
                price = new_price
    discountCoefficient = float(input("请输入打折日的折扣力度:"))
    product_info = {
        "name": name,
        "price": price, 
        "type": type,
        "discountCoefficient": discountCoefficient,
        "discountDay": random.randint(0,9),
        "firstRecordTime": datetime.now().isoformat(),
        "purchaseTime": ""
    }
    data = CheckProductFile()
    data.append(product_info)
    savejson(product_file_path,data)

def CheckProductFile():
    file_exists = os.path.exists(product_file_path)
    # 如果文件存在，读取已有数据
    if file_exists:
        with open(product_file_path, 'r',encoding='utf8') as file:
            data = json.load(file)
    else:
        data = []
    return data
def PurchaseProduct(cash):
    print("欢迎光临小店，当前余额{}".format(cash))
    # 检查文件是否存在
    data = CheckProductFile()
    ind = 0
    # 检查是否可以兑换商品
    dvalue,x = CanBuyOne(cash)
    canbuy = dvalue>0
    if not canbuy:
        print("不好意思，余额不能购买任何商品，继续加油吧")
        return cash
    else:
        for index,product in enumerate(data):
            price,hasUpdated = UpdateProductProperty(product)
            if price <= cash:
                print('可以兑换商品:{},价格:{},序号为:{}'.format(product['name'],product['price'],index))
            else:
                break
    # //【C】上面的 hasUpdated只是最后一次的值不能拿这个判断
    # if hasUpdated:
    #     savejson(product_file_path,data)
        # with open(product_file_path, 'w',encoding='utf8') as file:
        #     json.dump(data, file,ensure_ascii=False)

    ind = input('请输入要购买的商品序号(-1取消购买):')
    if ind == '-1':
        savejson(product_file_path,data)
        print("蟹蟹惠顾٩('ω')و")
        return cash
    
    ind = int(ind)
    product = data[ind]
    
    # 购买指定商品并更新cash值,打印信息
    if product['price'] > cash:
        print("余额不足(⊙︿⊙)")
        return cash
    cash -= product['price']
    product['purchaseTime'] = datetime.now().isoformat()
    print('已购买商品:{} 余额剩余:{}'.format(product['name'], cash))
    
    # 将原json种对应商品剔除掉更新json
    data.pop(ind)
    savejson(product_file_path,data)

    # with open(product_file_path, 'w') as file:
    #   json.dump(data, file,ensure_ascii=False)
      
    # 将购买的商品追加到purchased_product_file_pathjson中
    purchased_product_file_path = 'purchased_product.json'
    purchased_data = []
    if os.path.exists(purchased_product_file_path):
      with open(purchased_product_file_path, 'r',encoding='utf8') as file:
        purchased_data = json.load(file)
    purchased_data.append(product)
    savejson(purchased_product_file_path,purchased_data)

    # with open(purchased_product_file_path, 'w',encoding='utf8') as file:
    #   json.dump(purchased_data, file,ensure_ascii=False)
    print("蟹蟹惠顾٩('ω')و")
    return cash
#If discountDay is -1, randomly assign it to 0-9
# Get today's date
# Check if discountDay matches last digit of today's date
# If matches, update price by multiplying discountCoefficient
# Else return original price
def CanBuyOne(cash):
    data = CheckProductFile()
    data = sorted(data, key=lambda x: x['price'])
    savejson(product_file_path,data)
    return cash - data[0]['price'],data[0]['name']
#//【C】这个函数意义不大了
def UpdateProductProperty(product):
  hasUpdated = False
#   if product['firstRecordTime'] == "":
#     hasUpdated = True
#     product['firstRecordTime'] = datetime.now().isoformat()
  today = datetime.today()
  if product['discountDay'] == today.day % 10:
    product['price'] *= product['discountCoefficient']
    return product['price'],hasUpdated
  else:
    return product['price'], hasUpdated