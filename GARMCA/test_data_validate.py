from datetime import datetime
import copy
import file_io
# https://lyrichu.github.io/2018/06/10/sopt-%E4%B8%80%E4%B8%AA%E7%AE%80%E5%8D%95%E7%9A%84python%E6%9C%80%E4%BC%98%E5%8C%96%E5%BA%93/
import lp

y = []
x = []

if __name__ == "__main__":
    starttime = datetime.now()
    final_u = [0.6735939434838571, 0.7912919437320867,1.9131045871913426,1.2179302589477425,1.0448390793872917,
               0.169596840941467,0.030691038225475253,0.4414925822107576,1.4646116230206312]
    final_r = [[1.5281751,  1.40266785, 0.74523154 ,1.16001575],
               [1.00558568, 0.61719544 ,1.6462442 , 0.45635072],
               [1.2933611,  1.76916102, 0.95326572 ,1.72802422],
               [1.14138604 ,1.07698859, 0.12376278, 0.05308324],
               [0.12155121, 0.07603127, 0.16157069, 1.32137268],
               [1.50456013 ,1.90143328, 0.0030258 , 1.73270869],
               [0.02365309,1.54771774, 1.47278535 ,1.03314084],
               [0.38813154, 0.0740915,  1.8874048 , 1.48207334],
               [1.92683919, 1.7740166 , 1.42587921 ,0.56813736]
               ]

    # 读取数据
    data_num = file_io.loadDataFromFile("./data_test.bin", x, y)

    print("开始计算测试数据的收益：\nu : {0} \nr : {1}".format(final_u,final_r))
    payment_sum_i = 0
    payment_sum_vcg = 0
    vcg_count = 0
    for item_i in range(0, len(x)):
        item_x = copy.deepcopy(x[item_i])
        # 进行虚拟映射
        for bid_i in range(0, len(item_x)):
            r_num = 2 ** item_x[bid_i].item_num
            item_x[bid_i].virtual_price(final_u[bid_i], final_r[bid_i])
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
        payment_sum_vcg += payment_vcg
        # print("{0}：当前收益为{1}".format(item_i+1,payment_sum_i))

    print("计算{0}组数据,有{1}组为原始vcg分配,平均收益为{2},原始vcg收益为{3}".format(len(x),vcg_count,payment_sum_i / len(x),payment_sum_vcg / len(x)))

    # 计算程序花的时间
    endtime = datetime.now()
    print("程序运行时间 : {}".format(endtime - starttime))