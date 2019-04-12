#!/usr/bin/python
# -*- coding: UTF-8 -*-

import copy

"""
https://www.cnblogs.com/wilber2013/p/4645353.html
"""


def func(a):
    a.append('DDDD')


k = [1, 3, 4]

func(k)

print k
b = k
b = copy.copy(k)
b.remove("DDDD")
print k

will = ["Will", 28, ["Python", "C#", "JavaScript"]]
wilber = copy.deepcopy(will)

print id(will)
print will
print [id(ele) for ele in will]
print id(wilber)
print wilber
print [id(ele) for ele in wilber]

will[0] = "Wilber"
will[2].append("CSS")
print id(will)
print will
print [id(ele) for ele in will]
print id(wilber)
print wilber
print [id(ele) for ele in wilber]
