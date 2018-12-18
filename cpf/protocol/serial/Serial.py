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

    def __init__(self, device="/dev/ttyS0", baud=9600, timeout=1):
        """
        :param device:  串口设备
        :param baud:  波特率
        """
        self.ser = serial.Serial(device, baud, timeout=timeout)
        pass

    def recv(self, size=0):
        if size == 0:
            # 收的太快可能会收到空内容
            res = self.ser.read_all()
            while not res:
                res = self.ser.read_all()
                sleep(0.5)
        else:
            res = self.ser.read(size)
        return res

    def send(self, data):
        return self.ser.write(data)


if __name__ == '__main__':
    from cpf.misc.utils import hexdump

    com = Serial("/dev/ttyS0", 115200)
    com.send("\xaa\xbb\xcc\xdd\x20\x00\x00\x00\xbb\xcc\xdd")

    data = com.recv(1024)
    hexdump(data)
