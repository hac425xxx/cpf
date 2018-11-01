#!/usr/bin/env python
# encoding: utf-8

import parallel
# 这个库的函数，主要就是对 并口的 各个引脚进行设置
# 并口参考：https://wenku.baidu.com/view/b0e0ceea551810a6f52486ea.html

# 需要 modprobe -r lp ， 否则可能找不到设备
p = parallel.Parallel()


def write_data(data):
    p.setAutoFeed(0)
    p.setInitOut(0)
    for c in data:
        p.setDataStrobe(1)
        p.setData(ord(c))  # 数据总线为 8 位， 所以一次一个字节
        p.setDataStrobe(0)
        


print p.getInError() # print 1
print p.getInSelected() # print 1
print p.getInPaperOut() # print 0
print p.getInAcknowledge() #print 1
print p.getInBusy() # print False

write_data("abcd")

# 从 p2-9 读一个字节 
print chr(p.getData())

# 关闭数据总线，后面读到的数据为 0xff
p.setDataDir(0)
print hex(p.getData())

# 开启数据总线
p.setDataDir(1)
print chr(p.getData())