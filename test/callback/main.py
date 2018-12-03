#!/usr/bin/python
# -*- coding: UTF-8 -*-


def mutate(data, callback=None):
    ret = data
    if callback:
        ret = callback(data)

    print id(ret), id(data)
    return ret


def modify_callback(data):
    ret = data
    if "fuzz" in data:
        ret = data.replace("fuzz", "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")

    return ret


if __name__ == '__main__':
    print mutate('aaaaa', callback=modify_callback)
