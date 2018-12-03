#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: Mutater.py
@time: 2018/11/5 10:48
@desc: 提供一个接口，调用各种变异算法，完成数据变异
"""
from mangle import MANGLE_FUNCS
import mangle
from cpf.misc.utils import *


class Mutater:
    """  随机选取变异函数，对数据进行变异 """

    def __init__(self, mutate_max_count=6, token=[], callback=None):
        """
        :param mutate_max_count: 最大变异次数，程序会从 1，mutate_max_count 选取每次的变异次数
        :param token:  用于插入一些常量到数据里面
        """

        self.mutate_max_count = mutate_max_count
        self.mutate_funcs = MANGLE_FUNCS
        self.mutate_func_count = len(MANGLE_FUNCS)
        self.callback = callback
        mangle.TOKEN = token

    def mutate(self, data):
        """
        对 data 进行变异
        :param data:  待变异的数据
        :param callback: 对变异后的数据进行修正的callback 函数，比如 crc, header等
        :return:
        """
        # 选择变异次数
        count = random.randint(1, self.mutate_max_count)
        for i in xrange(count):
            # 随机选取一个变异函数
            func = self.mutate_funcs[random.randint(0, self.mutate_func_count - 1)]
            data = func(data)

        if self.callback:
            data = self.callback(data)
        return data


if __name__ == '__main__':
    mangle.TOKEN = ['\xde\xad\xbe\xef', '\x90\x90\x90\x90']

    import time

    mutater = Mutater()
    raw = "1234567890abcdefghijklmn"

    data = []

    start = time.time()
    for i in range(200000):
        hexdump(mutater.mutate(raw))

    end = time.time()

    print(len(list(set(data))))
    print("用时：{}".format(end - start))
