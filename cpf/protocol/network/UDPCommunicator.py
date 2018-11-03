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


class UDPCommunicator:
    """
    实现 udp 的基础通信
    """

    def __init__(self, ip, port):
        self.address = (ip, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def recv(self, size):
        try:
            self.s.settimeout(3)
            data, _ = self.s.recvfrom(size)
        except socket.timeout:
            data = ""
        return data

    def send(self, data):
        self.s.sendto(data, self.address)
        pass

    def is_dead(self):
        raise NotImplementedError("由于 udp 特殊性，请根据目标程序编写")

    def __del__(self):
        # print("调用析构函数， 关闭 socket")
        self.s.close()


if __name__ == '__main__':
    udp = UDPCommunicator("127.0.0.1", 9999)
    udp.send("ssssssssssssssssss")
    print(udp.recv(8))

    # print(udp.is_dead())
