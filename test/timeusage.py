#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import time

timestamp = 1462451334
time_local = time.localtime(timestamp)
dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

print dt

# 获取当前时间
time_now = int(time.time())
# 转换成localtime
time_local = time.localtime(time_now)
# 转换成新的时间格式(2016-05-09 18:59:20)
dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

print dt

import datetime

ts1 = int(time.time()) - 1000
ts2 = int(time.time())

# print datetime.datetime.fromtimestamp(ts2 - ts1)

old = datetime.datetime.fromtimestamp(int(time.time()) - 1000)
now = datetime.datetime.now()

delta = (now - old)

print (now - old)
