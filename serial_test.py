#!/usr/bin/env python
# encoding: utf-8
import serial
from time import sleep
ser = serial.Serial("/dev/ttyS0", 9600)


while True:
    input = raw_input("输入些东西，写到 串口的另一端：")
    ser.write(input)

    # 收的太快可能会收到空内容
    res = ser.read_all()
    while not res:
        res = ser.read_all()
        sleep(0.5)
    print("对方的回复：{}".format(res))

