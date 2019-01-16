#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: Serial.py
@time: 2018/11/1 22:04
@desc:
"""
import serial
from time import sleep
from cpf.protocol.Base import Base


class Serial(Base):
    """
    实现 串口 的基础通信
    """

    def __init__(self, device="/dev/ttyS0", baud=9600, timeout=1, interval=0.1):
        """
        :param device:  串口设备
        :param baud:  波特率
        """
        self.ser = serial.Serial(device, baud, timeout=timeout)
        self.interval = interval
        pass

    def recv(self, size=0):
        count = 0
        if size == 0:
            # 收的太快可能会收到空内容
            res = self.ser.read_all()
            while res == "" and count < 3:
                res = self.ser.read_all()
                sleep(0.5)
                count += 1
        else:
            res = self.ser.read(size)
        return res

    def send(self, data):
        sleep(self.interval)
        return self.ser.write(data)

    def recv_until(self, data):
        """
        返回到接收到 data 前所有接收的数据，一直到读完数据
        :param data:
        :return:
        """
        return self.ser.read_until(data)


if __name__ == '__main__':
    from cpf.misc.utils import hexdump

    # com = Serial("/dev/ttyS0", 115200)
    com = Serial("/dev/ttyACM0", 115200)

    com.send("aabbccddeeffgg")
    hexdump(com.recv())
    i = 0
    while True:
        i += 1
        # aabbccdd20000000bbccdd
        com.send("aabbccdd04000000bbccdd".decode("hex"))
        # hexdump(com.recv(1024))
        hexdump(com.recv_until("bbccdd".decode("hex")))

        print "count: {}".format(i)
