from docplex.mp.model import Model


# 判断数字第i位是否为1
def is_i_num(num, index):
    return bool(num & (1 << index))


def lp_func(bidders, bidder_num, items_num):
    # 线性规划求解
    # 1.构建MILP模型
    lp_model = Model('MILP')

    # 2.1 创建约束变量列表
    # 每一个人约束变量的个数
    var_num = 1 << items_num
    x_vars = {(i, j): lp_model.binary_var(name="x_{0}_{1}".format(i, j)) for i in range(0, bidder_num) if bidders[i].flag
              for j in range(0, var_num)}

    # 2.2添加每一个人只能分配一个物品的约束
    bidder_constraints = {i: lp_model.add_constraint(
        ct=lp_model.sum(x_vars[i, j] for j in range(0, var_num)) <= 1,
        ctname="bidder_constraint_{0}".format(i))
        for i in range(0, bidder_num) if bidders[i].flag}

    # 2.3添加一个物品只能被分配给一个人的约束
    item_constraints = {ii: lp_model.add_constraint(
        ct=lp_model.sum(x_vars[i, j] for i in range(0, bidder_num) if bidders[i].flag for j in range(0, var_num) if j & (1 << ii)) <= 1,
        ctname="item_constraint_{0}".format(ii))
        for ii in range(0, items_num)}

    # 3.定义目标函数
    obj_func = 0
    # 每一个人加上每一个物品
    for i in range(0, bidder_num):
        if bidders[i].flag:
            for j in range(0, var_num):
                obj_func += x_vars[i, j] * (bidders[i].u * bidders[i].bid_list_origin[j] + bidders[i].r[j])
    lp_model.set_objective('max', obj_func)
    #print(lp_model.lp_string)
    #lp_model.print_information()

    # 4.求解模型，输出结果
    lp_result = lp_model.solve()
    #lp_model.print_solution()
    return lp_result

def virtual_vcg(bidders):
    bidder_num = len(bidders)
    items_num = bidders[0].item_num
    var_num = 1 << items_num

    # 线性规划求解
    lp_result = lp_func(bidders, bidder_num, items_num)

    lp_result_dict = lp_result.iter_var_values()
    # print(lp_result.objective_value)
    # for lp_key in lp_result_dict:
    #     print(lp_key[0].safe_name, lp_key[0].safe_index)

    # 根据cplex结果进行计算
    max_price = lp_result.objective_value
    # 解析二维变量，x_0_2，代表bidder1选择第3个捆绑包
    for lp_key in lp_result_dict:
        # print(lp_key[0].safe_name, lp_key[0].safe_index)
        bidder_index = lp_key[0].safe_index // var_num
        item_index = lp_key[0].safe_index % var_num
        bidders[bidder_index].price = max_price
        # 临时过度
        # bidder_value = bidders[bidder_index].u * bidders[bidder_index].bid_list_origin[item_index] + \
        #                bidders[bidder_index].r[item_index]
        # bidders[bidder_index].payment = max_price - bidder_value + bidders[bidder_index].r[item_index]
        # 与上面的等价
        bidder_value = bidders[bidder_index].u * bidders[bidder_index].bid_list_origin[item_index]
        bidders[bidder_index].payment = max_price - bidder_value

    # 分别计算每一个人不参加情况下的最大社会福利
    for i in range(bidder_num):
        bidders[i].flag = False
        lp_result_tmp = lp_func(bidders, bidder_num, items_num)
        max_price_tmp = lp_result_tmp.objective_value
        bidders[i].payment = max_price_tmp - bidders[i].payment
        bidders[i].flag = True

    # 除以系数
    for i in range(bidder_num):
        temp = bidders[i].payment
        #print(i,bidders[i].payment)
        if temp <= 0:
            bidders[i].payment = 0
        else:
            bidders[i].payment = temp / bidders[i].u


# def virtual_vcg(bidders):
#     bidder_num = len(bidders)
#     items_num = bidders[0].item_num
#
#     # 线性规划求解
#     # 1.构建MILP模型
#     lp_model = Model('MILP')
#
#     # 2.1 创建约束变量列表
#     # 每一个人约束变量的个数
#     var_num = 1 << items_num
#     x_vars = {(i, j): lp_model.binary_var(name="x_{0}_{1}".format(i, j)) for i in range(0, bidder_num)
#               for j in range(0, var_num)}
#
#     # 2.2添加每一个人只能分配一个物品的约束
#     bidder_constraints = {i: lp_model.add_constraint(
#         ct=lp_model.sum(x_vars[i, j] for j in range(0, var_num)) <= 1,
#         ctname="bidder_constraint_{0}".format(i))
#         for i in range(0, bidder_num)}
#
#     # 2.3添加一个物品只能被分配给一个人的约束
#     item_constraints = {ii: lp_model.add_constraint(
#         ct=lp_model.sum(x_vars[i, j] for i in range(0, bidder_num) for j in range(0, var_num) if j & (1 << ii)) <= 1,
#         ctname="item_constraint_{0}".format(ii))
#         for ii in range(0, items_num)}
#
#     # 3.定义目标函数
#     obj_func = 0
#     # 每一个人加上每一个物品
#     for i in range(0, bidder_num):
#         for j in range(0, var_num):
#             obj_func += x_vars[i, j] * (bidders[i].u * bidders[i].bid_list_origin[j] + bidders[i].r[j])
#     lp_model.set_objective('max', obj_func)
#     # lp_model.print_information()
#
#     # 4.求解模型，输出结果
#     lp_result = lp_model.solve()
#     lp_model.print_solution()
#     lp_result_dict = lp_result.iter_var_values()
#     # print(lp_result.objective_value)
#     # for lp_key in lp_result_dict:
#     #     print(lp_key[0].safe_name, lp_key[0].safe_index)
#
#     # 根据cplex结果进行计算
#     max_price = lp_result.objective_value
#     # 解析二维变量，x_0_2，代表bidder1选择第3个捆绑包
#     for lp_key in lp_result_dict:
#         # print(lp_key[0].safe_name, lp_key[0].safe_index)
#         bidder_index = lp_key[0].safe_index // var_num
#         item_index = lp_key[0].safe_index % var_num
#         bidders[bidder_index].price = max_price
#         # 临时过度
#         bidder_value = bidders[bidder_index].u * bidders[bidder_index].bid_list_origin[item_index] + \
#                        bidders[bidder_index].r[item_index]
#         bidders[bidder_index].payment = max_price - bidder_value