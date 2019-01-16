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
import time
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
        data = ""
        try:
            self.s.settimeout(3)
            data, _ = self.s.recvfrom(size)
        except:
            self.s.settimeout(None)
        return data

    def recv_until(self, need, timeout=2):
        """
        读取到 need 返回所有读取的内容， 否则返回超时前读取的所有内容
        :param need: 需要的字符串
        :param timeout: 超时时间
        :return: 读取的内容
        """
        start = time.time()
        data = ""
        while need not in data:
            sleep(0.01)
            delta = time.time() - start
            if delta > timeout:
                return data
            data += self.recv(1024)
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
    udp.send("sssssssssssssssssssssssssss")
    print udp.recv_until("end", timeout=10)
