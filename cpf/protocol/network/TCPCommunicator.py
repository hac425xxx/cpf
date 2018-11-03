#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: TCPCommunicator.py
@time: 2018/11/2 20:30
@desc:
"""
import socket
from time import sleep
from cpf.protocol.Base import Base

class TCPCommunicator(Base):
    """
    实现 tcp 的基础通信
    """

    def __init__(self, ip, port):
        address = (ip, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(address)

    def recv(self, size):
        return self.s.recv(size)

    def send(self, data):
        self.s.send(data)
        pass

    def is_dead(self):
        """ 如果对方已经断开，返回 True """
        try:
            self.s.getsockname()
        except socket.error as err:
            err_type = err.args[0]
            if err_type == socket.errno.EBADF:  # 9: Bad file descriptor
                return True
        try:
            self.s.getpeername()
        except socket.error as err:
            err_type = err.args[0]
            if err_type in [socket.errno.EBADF, socket.errno.ENOTCONN]:  # 9: Bad file descriptor.
                return True  # 107: Transport endpoint is not connected

        return False

    def __del__(self):
        # print("调用析构函数， 关闭 socket")
        self.s.close()


if __name__ == '__main__':
    tcp = TCPCommunicator("127.0.0.1", 9998)
    while True:
        tcp.send("sssssssss")
        sleep(0.5)

        if tcp.is_dead():
            print("对方已断开")
            break
        print(tcp.recv(8))
