#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: Mutater.py
@time: 2018/11/5 10:48
@desc: 提供一个接口，调用各种变异算法，完成数据变异
"""
from mangle import MANGLE_FUNCS
import random
from utils import *


class Mutater:
    """  随机选取变异函数，对数据进行变异 """

    def __init__(self, mutate_count=6):
        """

        :param mutate_count:  最大变异次数
        """
        self.mutate_max_count = mutate_count
        self.mutate_funcs = MANGLE_FUNCS
        self.mutate_func_count = len(MANGLE_FUNCS)

    def mutate(self, data):
        # 根据开始设置的最大变异次数进行变异
        for i in xrange(self.mutate_max_count):
            # 随机选取一个变异函数
            func = self.mutate_funcs[random.randint(0, self.mutate_func_count - 1)]
            data = func(data)

        return data


if __name__ == '__main__':
    import time

    mutater = Mutater()
    raw = "1234567890abcdefghijklmn"

    start = time.time()
    for i in range(20000):
        data = mutater.mutate(raw)

    end = time.time()

    print("用时：{}".format(end - start))
