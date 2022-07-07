from docplex.mp.model import Model

# 创建数据 weight表示每个人的系数 add代表分配附加项
valuation = [[0, 1.78, 1.95, 3.04], [0, 1.46, 1.94, 3.77]]

# 两个人的系数，每个人的r都有 2的物品数量，跟每个估值对应的
# 这个是vcg的系数，通过带搜索参数，带来进行分配计算
u = [1, 1]
r = [[0, 0, 0, 0], [0, 0, 0, 0]]

items_number = len(valuation[0])

# 2.创建一个最优化模型
knapsack_model = Model('MILP')

# 3.添加多个二进制决策变量， binary_var_list(keys,lb=None,up=None,name=<type,'str'>,key_format=None)
# 可以一次添加很多变量，可以使用N，而不是写8行
# x0_0,x0_1,x0_2
x0 = knapsack_model.binary_var_list(items_number, name='x0')
# x1_0
x1 = knapsack_model.binary_var_list(items_number, name='x1')

# 4.添加约束
# 每个人最多获得一个捆绑包
knapsack_model.add_constraint((x0[0] + x0[1] + x0[2] + x0[3]) <= 1)
knapsack_model.add_constraint((x1[0] + x1[1] + x1[2] + x1[3]) <= 1)

# 新增组合约束，对于物品1来说，可能包含物品1的捆绑波包集合都小于1
# 这里有问题，下标需要计算，比如包含物品1的捆绑包有，第一个估值{1}，和第三个估值{1，2}，
# 需要考虑 xi[1]+xi[3]
knapsack_model.add_constraint((x0[1] + x0[3] + x1[1] + x1[3]) <= 1)
knapsack_model.add_constraint((x0[2] + x0[3] + x1[2] + x1[3]) <= 1)

# 5.定义目标函数
obj_fn = valuation[0][0]*x0[0]+valuation[0][1]*x0[1]+valuation[0][2]*x0[2]+valuation[0][3]*x0[3] + \
         valuation[1][0]*x1[0]+valuation[1][1]*x1[1]+valuation[1][2]*x1[2]+valuation[1][3]*x1[3]

# 虚拟映射目标函数
obj_fn1 = (u[0]*valuation[0][0]+r[0][0])*x0[0] + (u[0]*valuation[0][1]+r[0][1])*x0[1] + \
          (u[0]*valuation[0][2]+r[0][2])*x0[2] + (u[0]*valuation[0][3]+r[0][3])*x0[3] + \
          (u[1]*valuation[1][0]+r[1][0])*x1[0] + (u[1]*valuation[1][1]+r[1][1])*x1[1] + \
          (u[1]*valuation[1][2]+r[1][2])*x1[2] + (u[1]*valuation[1][3]+r[1][3])*x1[3]

knapsack_model.set_objective('max', obj_fn)
knapsack_model.print_information()

# 6.求解模型，输出结果
knapsack_model.solve()
knapsack_model.print_solution()