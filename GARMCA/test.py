def is_i_num(num,index):
    return bool(num&(1 << index))

print(is_i_num(0,0))
print(is_i_num(1,0))
print(is_i_num(2,0))
print(is_i_num(3,0))