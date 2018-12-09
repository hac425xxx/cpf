#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: UDPCommunicator.py
@time: 2018/11/2 21:19
@desc:
"""
import socket
from time import sleep
from cpf.protocol.Base import Base


class UDPCommunicator(Base):
    """
    实现 udp 的基础通信
    """

    def __init__(self, ip, port, interval=0.1):
        self.address = (ip, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.interval = interval

    def recv(self, size):
        self.s.settimeout(3)
        data, _ = self.s.recvfrom(size)
        self.s.settimeout(None)
        return data

    def send(self, data):
        sleep(self.interval)
        self.s.sendto(data, self.address)
        pass

    def __del__(self):
        # print("调用析构函数， 关闭 socket")
        self.s.close()


if __name__ == '__main__':
    udp = UDPCommunicator("127.0.0.1", 9999)
    while True:
        udp.send("ssssssssssssssssss")
        sleep(0.5)
    # print(udp.recv(8))

    # print(udp.is_dead())
