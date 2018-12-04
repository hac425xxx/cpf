#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: Base.py
@time: 2018/11/3 15:17
@desc:
"""


class Base:

    def recv(self, size):
        raise NotImplementedError("请实现该函数，函数作用为： 从目标获取数据， size 为最大数据长度")

    def send(self, data):
        raise NotImplementedError("请实现该函数，函数作用为：发送数据到目标， conf 为数据")

    def is_dead(self):
        raise NotImplementedError("请实现该函数，函数作用为：检测目标是否存活")
