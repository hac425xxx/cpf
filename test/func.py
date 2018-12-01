#!/usr/bin/python
# -*- coding: UTF-8 -*-


def f(l, i):
    tmp = []
    tmp += l
    tmp.append(i)
    print tmp


l = [1, 3, 4]

f(l, 1000)

print l
