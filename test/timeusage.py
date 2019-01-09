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




import datetime
i = datetime.datetime.now()
print ("当前的日期和时间是 %s" % i)
print ("ISO格式的日期和时间是 %s" % i.isoformat())
print ("当前的年份是 %s" % i.year)
print ("当前的月份是 %s" % i.month)
print ("当前的日期是  %s" % i.day)
print ("dd/mm/yyyy 格式是  %s/%s/%s" % (i.day, i.month, i.year))
print ("当前小时是 %s" % i.hour)
print ("当前分钟是 %s" % i.minute)
print ("当前秒是  %s" % i.second)

filename = "{}_{:02d}_{:02d}_{:02d}_{:02d}_{:02d}.log".format(i.year, i.month, i.day, i.hour, i.minute, i.second)
print filename

