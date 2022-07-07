import copy
from datetime import datetime
from math import sin

from sopt.GA.GA import GA
from sopt.util.functions import *
from sopt.util.ga_config import *
from sopt.util.constraints import *
from time import time

import file_io
import lp

x = []
y = []

def func1(params):
    global x
    global y
    vcg_count = 0
    # 对每一个数据进行虚拟映射，然后计算收益
    payment_sum_i = 0
    for item_i in range(0, len(x)):
        item_x = copy.deepcopy(x[item_i])
        # 进行虚拟映射
        for bid_i in range(0, len(item_x)):
            r_list = []
            r_num = 2**item_x[bid_i].item_num
            for ii in range(0, r_num):
                r_list.append(params[bid_i*(1+r_num)+1+ii])
            item_x[bid_i].virtual_price(params[bid_i*(1+r_num)], r_list)
        # 计算收益
        lp.virtual_vcg(item_x)
        # 计算ama的收益
        payment_i = 0
        for ii in item_x:
            payment_i += ii.payment
        # 计算原始vcg收益
        payment_vcg = 0
        for ii in item_x:
            payment_vcg += ii.vcg_payment
        # 计算全部训练数据的总收益
        if payment_i < payment_vcg:
            vcg_count += 1
            payment_i = payment_vcg
        payment_sum_i += payment_i

    delta = vcg_count / len(x) * 0.4
    return payment_sum_i / len(x) - delta

class TestGA:
    def __init__(self):
        self.func = func1
        self.func_type = 'max'
        self.variables_num = 10
        self.lower_bound = 0
        self.upper_bound = 2
        self.cross_rate = 0.8
        self.mutation_rate = 0.05
        self.generations = 10
        self.population_size = 100
        self.binary_code_length = 20
        self.cross_rate_exp = 1
        self.mutation_rate_exp = 1
        self.code_type = code_type.gray
        self.cross_code = False
        self.select_method = select_method.proportion
        self.rank_select_probs = None
        self.tournament_num = 2
        self.cross_method = cross_method.uniform
        self.arithmetic_cross_alpha = 0.1
        self.arithmetic_cross_exp = 1
        self.mutation_method = mutation_method.uniform
        self.none_uniform_mutation_rate = 1
        #self.complex_constraints = [constraints1,constraints2,constraints3]
        self.complex_constraints = None
        self.complex_constraints_method = complex_constraints_method.penalty
        self.complex_constraints_C = 1e6
        self.M = 1e8
        self.GA = GA(**self.__dict__)

    def test(self):
        start_time = time()
        self.GA.run()
        print("GA costs %.4f seconds!" % (time()-start_time))
        self.GA.save_plot()
        self.GA.show_result()

        # 打印结果
        bidder_num = len(x[0])
        r_num = 2 ** x[0][0].item_num
        print("-" * 20, "u and r:", "-" * 20)
        for i in range(0, len(x[0])):
            print("bidder [%d] :" % (i+1))
            #print(type(self.GA.global_best_point))
            print("u : {0}".format(self.GA.global_best_point[i*(1+r_num)]))
            print("r : {0}".format(self.GA.global_best_point[i*(1+r_num)+1 : (i+1)*(1+r_num)]))



if __name__ == '__main__':
    # 读取数据
    data_num = file_io.loadDataFromFile("./data_train.bin", x, y)

    starttime = datetime.now()
    TestGA().test()
    # 计算程序花的时间
    endtime = datetime.now()
    print("程序运行时间 : {}".format(endtime - starttime))