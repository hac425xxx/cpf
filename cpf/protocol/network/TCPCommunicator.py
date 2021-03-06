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
import time
from cpf.protocol.Base import Base


class TCPCommunicator(Base):
    """
    实现 tcp 的基础通信
    """

    def __init__(self, ip, port, interval=0, retry_interval=0.3, retry_count=3):
        """

        :param ip: 目标 ip
        :param port: 目标端口
        :param interval: 每次发包的间隔，会在 send 前 sleep 一下
        :param retry_interval: 出现连接错误时等待的时间间隔， 实际等待时间： retry_interval * count
        """
        address = (ip, port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        count = 1
        while count <= retry_count:
            try:
                self.s.connect(address)
                break
            except Exception as e:
                # print e
                # print("连接失败，{} 秒后尝试重连!!!".format(retry_interval * count))
                sleep(retry_interval * count)
                count += 1

        if count > 3:
            raise Exception("创建连接失败， 请确定目标服务已经开启")
        self.interval = interval

        sleep(0.01)

    def recv(self, size, timeout=2.0):
        data = ""
        try:
            self.s.settimeout(timeout)
            data = self.s.recv(size)
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
    now = time.time()
    tcp = TCPCommunicator("127.0.0.1", 9998)
    print tcp.recv_until("end", timeout=10)

    print "运行: {}".format(time.time() - now)
