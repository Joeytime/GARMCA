import copy
from datetime import datetime
import matplotlib.pyplot as plt

from math import sin

import pygad
from time import time

import file_io
import lp

x = []
y = []


def fitness_function(params, solution_idx):
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
            r_num = 2 ** item_x[bid_i].item_num
            for ii in range(0, r_num):
                r_list.append(params[bid_i * (1 + r_num) + 1 + ii])
            item_x[bid_i].virtual_price(params[bid_i * (1 + r_num)], r_list)
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

    delta = vcg_count / len(x) * 0.6
    return payment_sum_i / len(x) - delta


if __name__ == '__main__':
    # 读取数据
    data_num = file_io.loadDataFromFile("./data_train.bin", x, y)

    starttime = datetime.now()

    # 搜索代数
    num_generations = 120
    num_parents_mating = 4
    # 种群数量
    sol_per_pop = 20
    # 参数个数
    num_genes = 45

    init_range_low = 0
    init_range_high = 2

    parent_selection_type = "sss"
    keep_parents = 1

    crossover_type = "single_point"

    mutation_type = "random"
    mutation_percent_genes = 2
    # mutation_type = "adaptive"
    # mutation_percent_genes = (15, 8)
    # mutation_num_genes = (3, 1)

    # 参数取值范围
    gene_space = {'low': 0, 'high': 2}
    ga_instance = pygad.GA(num_generations=num_generations,
                           num_parents_mating=num_parents_mating,
                           gene_space=gene_space,
                           fitness_func=fitness_function,
                           sol_per_pop=sol_per_pop,
                           num_genes=num_genes,
                           init_range_low=init_range_low,
                           init_range_high=init_range_high,
                           parent_selection_type=parent_selection_type,
                           keep_parents=keep_parents,
                           crossover_type=crossover_type,
                           mutation_type=mutation_type,
                           mutation_percent_genes=mutation_percent_genes)
    ga_instance.save_solutions = True
    ga_instance.run()

    fitness = ga_instance.plot_fitness()
    fitness.savefig("fitness.png")
    fitness.show()

    new_solution_rate = ga_instance.plot_new_solution_rate()
    new_solution_rate.savefig("new_solution_rate.png")
    new_solution_rate.show()

    # gene = ga_instance.plot_genes(graph_type="plot",
    #                        plot_type="plot")
    # gene.savefig("gene.png")
    # gene.show()
    #
    # gene_value = ga_instance.plot_genes(graph_type="boxplot",
    #                        solutions='all')
    # gene_value.savefig("gene_value.png")
    # gene_value.show()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))

    # 格式化打印结果
    # 打印结果
    bid_num = len(x[0])
    r_num = 2 ** x[0][0].item_num
    print("-" * 20, "u and r:", "-" * 20)
    for i in range(0, len(x[0])):
        print("bidder [%d] :" % (i + 1))
        print("u : {0}".format(solution[i * (1 + r_num)]))
        print("r : {0}".format(solution[i * (1 + r_num) + 1: (i + 1) * (1 + r_num)]))
    # 计算程序花的时间
    endtime = datetime.now()
    print("程序运行时间 : {}".format(endtime - starttime))
