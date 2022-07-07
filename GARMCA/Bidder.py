import random
from datetime import datetime
import itertools
import copy

class Bidder:

    def __init__(self,bidder_id=0):
        self.bidder_id = bidder_id
        # 2^n个物品价格的列表 [0,0.1,0.2,0.3]
        self.bid_list = list()
        # 物品价格的备份，ama时候会用到
        self.bid_list_origin = list()
        # 物品的个数
        self.item_num = 0
        # 2^n个物品组合的列表[[0,0],[0,1],[1,0],[1,1]]
        self.num_list = list()
        # 参加情况下买的东西
        self.own_bid_list = list()
        # 当前报价
        self.price = 0
        # 支付
        self.vcg_payment = 0
        self.payment = 0
        # 标记有没有参加
        self.flag = True
        # 虚拟映射系数
        self.u = 0
        self.r = []
        # 社会最大福利
        self.sw = 0

    # 整数num转长度为num_len的2进制数组   3 -> [1,1]
    def int2array(self, num, num_len):
        #转为成二进制str，3->'11'
        bin_str = bin(num).replace('0b', '').rjust(num_len, '0')
        rs = []
        #将字符串转换成list,'11'->[1,1]
        for i in range(len(bin_str)):
            rs.append(int(bin_str[len(bin_str) - i - 1]))
        return rs

    # 整数num转长度为num_len的2进制数组   3 -> [1,1]
    def array2int(self, num_list):
        rs = 0
        cof = 1
        len_tmp = len(num_list) - 1
        while len_tmp >= 0:
            rs += num_list[len_tmp]*cof
            cof*=2
            len_tmp -= 1
        return rs

    # 为每个bidder生成报价列表
    def create_bids(self,items_num,bid_func,c_func):

        self.item_num = items_num
        # 生成物品的下标列表，那个位置是1，哪个物品买了。1左移0，1，2次；2个物品，
        # [1,2,4] 1=001，2：010 4：100

        # 生成报价0，[0,0]
        self.bid_list.append(0)
        self.num_list.append(self.int2array(0, items_num))

        # 设置暂时单价、下标列表
        temp_bid_list = []
        # [1,2,4]
        temp_num_list = [1 << x for x in range(items_num)]

        # 生成单个物品的报价
        for i in range(items_num):
            # 对每一个物品生成其分布的报价,保留2位有效小数
            temp_bid = float('%.2f' % bid_func())
            temp_bid_list.append(temp_bid)
            self.bid_list.append(temp_bid)
            # i=0，把一个数字转化成一个列表。5：101
            self.num_list.append(self.int2array(1 << i, items_num))

        # 对物品报价进行排列组合,从2个物品开始
        for combina_num in range(2, items_num + 1):
            # 从temp_num_list[1,2,4]中选取combina_num数量个进行组合
            for item1 in itertools.combinations(temp_num_list, combina_num):
                self.num_list.append(self.int2array(sum(item1), items_num))
            # temp_bid_list[0.1,0.2,0.4]中选取combina_num数量个进行组合相加,加上偏置c
            for item2 in itertools.combinations(temp_bid_list, combina_num):
                temp_bid_c = float('%.2f' % c_func())
                self.bid_list.append(sum(item2)+temp_bid_c)


    def print(self):
        for i in range(len(self.num_list)):
            print("第{}种出价，购买物品{}，出价{}".format(i + 1, self.num_list[i], self.bid_list[i]))

    def virtual_price(self,u,r):
        # 备份数据
        self.bid_list_origin = copy.deepcopy(self.bid_list)
        self.vcg_payment = self.payment
        # 记录虚拟映射参数
        self.u = u
        self.r = copy.deepcopy(r)
        # 虚拟估值
        for i in range(len(self.bid_list)):
            value = u*self.bid_list[i]
            if value < 0:
                self.bid_list[i] = 0
            else:
                self.bid_list[i] = value


    def getOriginPrice(self):
        index = self.array2int(self.own_bid_list)
        return self.bid_list_origin[index]