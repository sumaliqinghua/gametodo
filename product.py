#原价 折扣
#读取待售商品
#随机掉落限时折扣，如果在xx时间内完成下一个番茄商品降价
# # 用户数据
from datetime import datetime
import json
import os
import random
from statics import show_today_stats, total_stats

purchased_product_file_path = 'json/purchased_product.json'

product_file_path = 'json/product.json'
product_type_dict = {
        '1': '娱乐',
        '2': '服装',
        '3': '健康',
        '4': '出行',
        '5': '教育',
        '6': '数码',
        '7': '礼物',
        '8': '家居',
        '9': '美食',
        '10': '美妆',
        '11': '宠物',
        '12': '虚拟',
        '13': '其他',
        # //【?】虚拟的单独一类？
    }
# product = {
#       "name": "厚帽子",
#       "price": 15.0,
#       "type": "其他",
#       "discountCoefficient": 0.8,
#       "comments": "厚帽子，防风保暖",
#       "discountDay": -1,#折扣日 日期个位正好和价格个位数相等 0.6-0.99折扣
#       "firstRecordTime": "",#添加产品后首次记录番茄的时间
#       "purchaseTime": "",
#       "writeoffTime": "",
#     }

class Product:
  
  def __init__(self, name, price, type, discountCoefficient, comments, discountDay = -1, firstRecordTime ='', purchaseTime ='', writeoffTime = ''):
    self.name = name
    self.price = price
    self.type = type
    self.discountCoefficient = discountCoefficient
    self.comments = comments
    self.discountDay = discountDay if discountDay >= 0 else random.randint(0, 9)
    self.firstRecordTime = firstRecordTime if firstRecordTime else datetime.now().isoformat()
    self.purchaseTime = purchaseTime
    self.writeoffTime = writeoffTime
    
  def get_price(self):
    price = self.price
    if self.is_discount():
        price *= self.discountCoefficient
    return price
  def is_discount(self):
    return self.discountDay == datetime.today().day % 10
        
# 修改后的数据存储
products = [] 

def ExchangeProduct():
    while True:
        notwriteoff_index = []
        purchased_data = load_products(purchased_product_file_path)
        for index,product in enumerate(purchased_data):
            if product.writeoffTime == "":
                notwriteoff_index.append(index)
        if len(notwriteoff_index) != 0:
            print("还未核销的商品有:")
            for index in notwriteoff_index:
                product = purchased_data[index]
                print('{}:{}'.format(index,product.name))
        else:
            print("所有商品都已核销")
            break
        product_index = int(input("请输入要核销的商品序号:"))
        if product_index in notwriteoff_index:
            product = purchased_data[product_index]
            product.writeoffTime = str(datetime.today())
            print("核销 {} 成功".format(product.name))
            check = input("是否继续核销商品?(y/n)")
            if check == 'n':
                break
            else:
                # while true又要重新读取所以此处得保存
                savejson(purchased_product_file_path,purchased_data)
                continue
        else:
            print("商品无法核销")
            break
    savejson(purchased_product_file_path,purchased_data)

    purchased_data.append(product)
def GotoStore(user):
    print("欢迎来到商品商城")
    while True:
        print("1.录入商品")
        print("2.核销商品")
        print("3.购买商品")
        print("4.取消")
        choice = input("请输入选项:")
        if choice == "1":
            RecordProduct()
            continue
        elif choice == "2":
            ExchangeProduct()
            continue
        elif choice == "3":
            cash = PurchaseProduct(user.coins)
            user.coins = cash
            user.save_user_data()
            show_today_stats()
            continue
        elif choice == "4":
            break
        else:
            print("输入错误")
            continue

def RecordProduct():
    name = input("请输入商品名称:")
    for i in range(len(product_type_dict)):
        print(i+1,":",product_type_dict[str(i+1)])
    type = input("请选择商品分类:")
    type = product_type_dict[type]
    comments = input("请输入商品备注:")
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
    product = Product(name, price, type, discountCoefficient, comments) 
    data = load_products()
    data.append(product)
    savejson(product_file_path,data)
def savejson(file_path,products):
    product_dicts = [product.__dict__ for product in products] 
    with open(file_path, 'w', encoding='utf-8') as output:
        json.dump(product_dicts, output, indent=4, ensure_ascii=False)
# 新加一个从json加载产品列表的函数  
def load_products(file_path = 'json/product.json'):

  file_exists = os.path.exists(file_path)
  
  if file_exists:
    with open(file_path, encoding='utf-8') as f:
      product_dicts = json.load(f)

    products = [Product(d['name'], d['price'], d['type'], d['discountCoefficient'], d['comments'], d['discountDay'], d['firstRecordTime'], d['purchaseTime'], d['writeoffTime']) 
                for d in product_dicts]
  else:
    products = []

  return products

def PurchaseProduct(cash):
    print("欢迎光临小店，当前余额{}".format(cash))
    # 检查文件是否存在
    data = load_products()
    ind = 0
    # 检查是否可以兑换商品
    dvalue,x = CanBuyOne(cash)
    canbuy = dvalue>0
    if not canbuy:
        print("不好意思，余额不能购买任何商品，继续加油吧")
        return cash
    else:
        for index,product in enumerate(data):
            if product.get_price() <= cash:
                print('可以兑换商品:{},价格:{},序号为:{}'.format(product.name,product.get_price(),index))
            else:
                break

    ind = input('请输入要购买的商品序号(-1取消购买):')
    if ind == '-1':
        savejson(product_file_path,data)
        print("蟹蟹惠顾٩('ω')و")
        return cash
    
    ind = int(ind)
    product = data[ind]
    
    # 购买指定商品并更新cash值,打印信息
    if product.get_price() > cash:
        print("余额不足(⊙︿⊙)")
        return cash
    cash -= product.get_price()
    product.purchaseTime = datetime.now().isoformat()
    print('已购买商品:{} 余额剩余:{}'.format(product.name, cash))
    
    # 将原json种对应商品剔除掉更新json
    data.pop(ind)
    savejson(product_file_path,data)
      
    # 将购买的商品追加到purchased_product_file_pathjson中
    purchased_data = load_products(purchased_product_file_path)
    purchased_data.append(product)
    savejson(purchased_product_file_path,purchased_data)

    # with open(purchased_product_file_path, 'w',encoding='utf8') as file:
    #   json.dump(purchased_data, file,ensure_ascii=False)
    print("蟹蟹惠顾٩('ω')و")
    return cash

def CanBuyOne(cash):
    data = load_products()
    data = sorted(data, key=lambda x: x.get_price())
    savejson(product_file_path,data)
    return cash - data[0].get_price(),data[0].name
def show_products():
    data = load_products()
    data = sorted(data, key=lambda x: x.get_price())
    products_list = []
    for product in data:
        products_list.append({
            'name': product.name,
            'price': product.get_price(),
            'type': product.type,
            'description': product.comments,
            'discount': product.discountCoefficient if product.is_discount() else 1.0
        })
    return products_list
def show_discount_products():
    data = load_products()
    data = sorted(data, key=lambda x: x.get_price())
    # savejson(product_file_path,data)
    print('打折商品列表:')
    for index,product in enumerate(data):
        if product.is_discount():
            print('{}. {} 折扣:{}'.format(index,product.name,product.discountCoefficient))