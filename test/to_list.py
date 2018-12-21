#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: to_list.py
@time: 2018/11/3 20:30
@desc:
"""

with open("data", "r") as fp:
    data = fp.readlines()

# res = "["
# count = 0
# for line in data:
#     count += 1
#     res += '"{}",'.format(line.strip())
#
# res = res[:-1] + "]"
# print(count)
# print(len(res))
# print(res)

res = "["
for i in range(256):
    res += '"\\x{:02x}",'.format(i)

res = res[:-1] + "]"
print(res)
