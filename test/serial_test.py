#!/usr/bin/env python
# encoding: utf-8
import serial
from time import sleep

ser = serial.Serial("/dev/ttyS0", 115200)

while True:

    # 收的太快可能会收到空内容
    res = ser.read_all()
    while not res:
        res = ser.read_all()
        sleep(0.5)

    print("对方的回复：{}".format(res))
