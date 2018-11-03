#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: Parallel.py
@time: 2018/11/1 22:13
@desc:
"""
import parallel

from cpf.protocol.Base import Base


class Parallel(Base):
    """
    实现 并口 的基础通信
    """

    def __init__(self, port=0):
        # 需要 modprobe -r lp  安装内核模块， 否则可能找不到设备
        self.p = parallel.Parallel(port)

    def send(self, data):
        self.p.setAutoFeed(0)
        self.p.setInitOut(0)
        for c in data:
            self.p.setDataStrobe(1)
            self.p.setData(ord(c))  # 数据总线为 8 位， 所以一次一个字节
            self.p.setDataStrobe(0)

    def recv(self, size=1):
        return self.p.getData()


if __name__ == '__main__':
    p = Parallel()
    p.send("kkkllllxxxxb")
    print(chr(p.recv()))

    p.is_dead()
