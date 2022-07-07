from Bidder import *
from datetime import datetime
import copy
from functools import partial
import random

def int2array(num, num_len):
    bin_str = bin(num).replace('0b', '').rjust(num_len, '0')
    rs = []
    for i in range(len(bin_str)):
        rs.append(int(bin_str[len(bin_str) - i - 1]))
    return rs

def array2int(num_list,base = 2):
    rs = 0
    cof = 1
    i = 0
    while i < len(num_list):
        rs += num_list[i]*cof
        cof*=base
        i+=1
    return rs

def array2int_reverse(num_list,base = 3):
    rs = 0
    cof = 1
    i = len(num_list) - 1
    while i >= 0:
        rs += num_list[i]*cof
        cof*=base
        i -= 1
    return rs

def checkBid(total, bid_a):
    for i in range(len(total)):
        if total[i] == 0 and bid_a[i] == 1:
            return False
    return True

def removeItem(total, bid_a):
    for i in range(len(total)):
        if bid_a[i] == 1:
            total[i] = 0

def addItem(total, bid_a):
    for i in range(len(total)):
        if bid_a[i] == 1:
            total[i] = 1

# 定义物品数量
items_num = 2
# 定义拍卖者数量
bidder_num = 9
# 定义每一个人的分布函数
bid_func_list = [partial(random.uniform, 0,1), partial(random.uniform, 0,1), partial(random.uniform,0,1),
                 partial(random.uniform, 0,1), partial(random.uniform, 0,1), partial(random.uniform, 0,1),
                 partial(random.uniform, 0,1),partial(random.uniform, 0,1),partial(random.uniform, 0,1)]
# 定义C函数
bid_c_func = partial(random.uniform, -1, 1)
# 定义拍卖者数组，Bidder类型的列表
bidders = []

bid_num = (1 << items_num)-1
items_list = int2array(bid_num,items_num)
max_price = 0
max_price_list = []
max_price_bid = []
# 当前的物品分配
g_cur_auction_list = []

# 搜索最优分配，索引，价格，报价列表
def search(bidder_index,price, bid_list, price_list):
    global max_price
    global max_price_bid
    global max_price_list
    # 终止条件：如果投标人索引>=投标人数量
    if bidder_index >= bidder_num:
        return
    # 初始化
    if bidder_index == 0:
        max_price = 0
        max_price_list = []
        max_price_bid = []
    if bidders[bidder_index].flag:
        # 对每个投标进行搜索
        for i in range(bid_num+1):
            if checkBid(items_list, bidders[bidder_index].num_list[i]):
                bid_list.append(bidders[bidder_index].num_list[i])
                price_list.append(bidders[bidder_index].bid_list[i])
                price += bidders[bidder_index].bid_list[i]

                # 记录最好的结果
                if price >= max_price:
                    max_price_bid = copy.deepcopy(bid_list)
                    max_price_list = copy.deepcopy(price_list)
                    # print("#####",max_price_bid)
                    max_price = price

                # 尝试继续迭代
                removeItem(items_list,bidders[bidder_index].num_list[i])
                search(bidder_index+1,price,bid_list,price_list)

                bid_list.pop()
                price_list.pop()
                addItem(items_list, bidders[bidder_index].num_list[i])
                price -= bidders[bidder_index].bid_list[i]
    else:
        bid_list.append(bidders[bidder_index].num_list[0])
        price_list.append(0)

        # 记录最好的结果
        if price >= max_price:
            max_price_bid = copy.deepcopy(bid_list)
            max_price_list = copy.deepcopy(price_list)
            # print("#####",max_price_bid)
            max_price = price
        search(bidder_index + 1, price, bid_list, price_list)

        bid_list.pop()
        price_list.pop()

def generateData(times,data_x,data_y,print_flag = 1,sort_flag = False):
    global bidders
    for ii in range(times):
        if print_flag:
            print("第{}次拍卖".format(ii + 1))
        # 初始化每一个投标人，并打印
        bidders = []
        for i in range(bidder_num):
            temp_bidder = Bidder(i + 1)
            temp_bidder.create_bids(items_num, bid_func_list[i], bid_c_func)
            bidders.append(temp_bidder)
            if print_flag:
                print("用户{}的报价 : ".format(i + 1))
                temp_bidder.print()
        # 记录所有人的报价
        data_x.append(bidders)

        # 搜索每个人都参加的情况下的最大社会福利跟报价
        search(0, 0, [], [])
        #print("###########\n{}\n{}\n{}\n################".format(max_price, max_price_bid, max_price_list))

        for i in range(bidder_num):
            bidders[i].price = max_price_list[i]
            bidders[i].sw = max_price
            # 临时过度
            bidders[i].payment = max_price - max_price_list[i]
            bidders[i].own_bid_list = copy.deepcopy(max_price_bid[i])

        #print("社会最大福利：{0}".format(max_price))

        # 不参加情况下的最大社会福利
        for i in range(bidder_num):
            bidders[i].flag = False
            search(0, 0, [], [])
            #print("************\n{}\n{}\n{}\n*************".format(max_price, max_price_bid, max_price_list))
            bidders[i].payment = max_price - bidders[i].payment
            bidders[i].flag = True

        total_payment = 0
        for i in range(bidder_num):
            payment_list = []
            total_payment = total_payment + bidders[i].payment
            if print_flag:
                print("用户{}购买{}商品，报价为{}，实际支付{}".format(i + 1, bidders[i].own_bid_list, bidders[i].price, bidders[i].payment))
            payment_list.append(bidders[i].payment)

        if print_flag:
            print("总支付为{}".format(total_payment))

        # 根据是否需要排序标识进行排序
        if sort_flag:
            bidders.sort(key=lambda x: x.payment, reverse=False)
        # 记录本次的支付
        data_y.append(total_payment)

    # 计算平均收益
    print("{0}组数据的平均收益为{1}".format(times,sum(data_y)/times))
    # 设置初始系数
    m = []
    for ii in range(bidder_num):
        m.append(1)
    return m

if __name__ == "__main__":
    print("物品种类为{}，参与拍卖者的数量为{}".format(items_num, bidder_num))
    starttime = datetime.now()
    # 初始化每一个投标人，并打印
    for i in range(bidder_num):
        temp_bidder = Bidder(i + 1)
        temp_bidder.create_bids(items_num, bid_func_list[i], bid_c_func)
        bidders.append(temp_bidder)

        print("用户{}的报价 : ".format(i + 1))
        temp_bidder.print()

    # 搜索每个人都参加的情况下的最大社会福利跟报价
    search(0, 0, [], [])
    print("###########\n{}\n{}\n{}\n################".format(max_price, max_price_bid, max_price_list))

    for i in range(bidder_num):
        bidders[i].price = max_price_list[i]
        bidders[i].sw = max_price
        # 临时过度
        bidders[i].payment = max_price - max_price_list[i]
        bidders[i].own_bid_list = copy.deepcopy(max_price_bid[i])

    print("社会最大福利：{0}".format(max_price))

    # 不参加情况下的最大社会福利
    for i in range(bidder_num):
        bidders[i].flag = False
        search(0, 0, [], [])
        print("************\n{}\n{}\n{}\n*************".format(max_price,max_price_bid,max_price_list))
        bidders[i].payment = max_price - bidders[i].payment
        bidders[i].flag = True

    total_payment = 0
    for i in range(bidder_num):
        total_payment = total_payment + bidders[i].payment
        print("用户{}购买{}商品，报价为{}，实际支付{}".format(i+1,bidders[i].own_bid_list,bidders[i].price,bidders[i].payment))

    print("总支付为{}".format(total_payment))

    # 计算程序花的时间
    endtime = datetime.now()
    print ("程序运行时间 : {}".format(endtime - starttime))