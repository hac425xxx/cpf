#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: L3Communicator.py
@time: 2018/11/3 10:01
@desc:
"""
import scapy.all as scapy
from cpf.protocol.Base import Base

class L3Communicator(Base):
    """
    在 ip 层通信的类，直接发送 ip 层的数据包
    """

    def __init__(self, dst, iface):
        """

        :param dst:  目标 ip 地址
        :param iface:  发送数据包的接口
        """
        self.iface = iface
        self.dst = dst


    def send(self, data):
        # 首先构造好 以太网层 和 ip 层的数据
        # l2 = scapy.Ether()
        # l3 = scapy.IP(dst=self.dst)
        #
        # pkt = (l2 / l3).build() + data
        # scapy.sendp(pkt, iface=self.iface)

        # 使用 send ， 确保下层的结构完整
        scapy.send(scapy.IP(dst=self.dst) / data)


if __name__ == '__main__':
    l3 = L3Communicator("192.168.3.22", "ens38")
    l3.send("s" * 40)
