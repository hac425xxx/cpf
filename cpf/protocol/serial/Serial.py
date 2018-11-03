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

    def __init__(self, device="/dev/ttyS0", baud=9600):
        """
        :param device:  串口设备
        :param baud:  波特率
        """
        self.ser = serial.Serial(device, baud)
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
    com = Serial("/dev/ttyS0", 9600)
    com.send("k" * 8)
    while True:
        print(com.recv())
