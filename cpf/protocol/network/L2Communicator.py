#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: L2Communicator.py
@time: 2018/11/3 9:56
@desc:
"""
import scapy.all as scapy

from cpf.protocol.Base import Base


class L2Communicator(Base):
    """
    允许用户直接发送以太网的数据包
    """

    def __init__(self, iface):
        """

        :param iface:  指定数据从哪个网卡发送，比如 ens33
        """
        self.iface = iface

    def recv(self, size):
        pass

    def send(self, data):
        scapy.sendp(data, iface=self.iface)


if __name__ == '__main__':
    l2 = L2Communicator("ens38")
    l2.send("k" * 80)
