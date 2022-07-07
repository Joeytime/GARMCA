from datetime import datetime
import copy
import xlwt
import vcg
import pickle

# 需要持久化数据的数量
data_num = 1000
# 生成测试集还是训练集
# 1为train训练集，0为test测试集
train_flag = 0

# 一组拍卖内部是否需要排序
sort_flag = True

def loadDataFromFile(excel_path, x, y):
    print("load from file {0}".format(excel_path))
    mydb = open(excel_path, 'rb')
    x_tmp = pickle.load(mydb)
    y_tmp = pickle.load(mydb)
    for ii in x_tmp:
        x.append(ii)
    for ii in y_tmp:
        y.append(ii)
    mydb.close()
    return len(x)


if __name__ == "__main__":

    file = xlwt.Workbook(encoding='utf-8')
    # 指定file以utf-8的格式打开
    sheet1 = file.add_sheet('vcg',cell_overwrite_ok=True)

    # 数据的配置
    config_data_name = ["物品数", "买家数", "总拍卖数"]
    config_data = [2, 9, data_num]
    for i in range(0, len(config_data)):
        sheet1.write(i, 0, config_data_name[i])
        sheet1.write(i, 1, config_data[i])

    # 生成模拟数据
    y = []
    x = []

    m = vcg.generateData(config_data[2], x, y, 0, sort_flag)

    # 指定标题
    head = ['序号']
    # 生成标题
    # 用户
    for i in range(config_data[1]):
        # 物品
        jj = 1<<config_data[0]
        for j in range(jj):
            str1 = "用户{0}对物品{1}的报价".format(i+1,x[0][0].num_list[j])
            head.append(str1)

    # 拍卖结果
    for i in range(config_data[1]):
        str2 = "用户{0}购买的物品".format(i + 1)
        head.append(str2)
        str2 = "用户{0}的报价".format(i + 1)
        head.append(str2)
        str2 = "用户{0}的支付".format(i + 1)
        head.append(str2)

    # 最大社会福利
    str3 = "最大社会福利"
    head.append(str3)

    # print(head)
    # 添加标题
    for i in range(0, len(head)):
        # 设置列宽
        fir_col = sheet1.col(i)  # 设置首列的宽度
        fir_col.width = 256*22
        # 写入标题
        sheet1.write(4, i, head[i])

    # # 参加情况下买的东西
    # self.own_bid_list = list()
    # # 当前报价
    # self.price = 0
    # # 支付
    # self.payment = 0
    # # 标记有没有参加
    # self.flag = True

    for i in range(config_data[2]):
        # 写入数据
        sheet1.write(i+5, 0, i+1)
        # 用户
        for ii in range(config_data[1]):
            # 物品
            for jj in range(len(x[i][ii].bid_list)):
                sheet1.write(i + 5, ii*len(x[i][ii].bid_list)+jj+1, x[i][ii].bid_list[jj])

        # 运行结果
        for ii in range(config_data[1]):
            sheet1.write(i + 5, config_data[1]*(1<<config_data[0]) + 1 + ii*3, "{0}".format(x[i][ii].own_bid_list))
            sheet1.write(i + 5, config_data[1]*(1<<config_data[0]) + 2 + ii*3, x[i][ii].price)
            sheet1.write(i + 5, config_data[1]*(1<<config_data[0]) + 3 + ii*3, x[i][ii].payment)

        # 最大社会福利
        sheet1.write(i + 5, config_data[1] * (1 << config_data[0]) + 1 + config_data[1] * 3, x[i][ii].sw)

    file_name = ""
    if train_flag:
        file_name = "data_train.xls"
    else:
        file_name = "data_test.xls"
    file.save(file_name)

    # 序列化到本地
    file_name = ""
    if train_flag:
        file_name = "data_train.bin"
    else:
        file_name = "data_test.bin"
    mydb = open(file_name, 'wb')
    pickle.dump(x, mydb)
    pickle.dump(y, mydb)
    mydb.close()