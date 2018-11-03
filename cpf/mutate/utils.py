#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: utils.py
@time: 2018/11/3 18:15
@desc: 一些变异模块可能需要的小函数
"""
import random
from struct import pack, unpack


def p8(d):
    """Return d packed as 8-bit unsigned integer (little endian)."""
    d = d & 0xff
    return pack('<B', d)


def u8(d):
    """Return the number represented by d when interpreted as a 8-bit unsigned integer (little endian)."""
    return unpack('<B', d)[0]


def p16(d):
    """Return d packed as 16-bit unsigned integer (little endian)."""
    d = d & 0xffff
    return pack('<H', d)


def u16(d):
    """Return the number represented by d when interpreted as a 16-bit unsigned integer (little endian)."""
    return unpack('<H', d)[0]


def p32(d):
    """Return d packed as 32-bit unsigned integer (little endian)."""
    d = d & 0xffffffff
    return pack('<I', d)


def u32(d):
    """Return the number represented by d when interpreted as a 32-bit unsigned integer (little endian)."""
    return unpack('<I', d)[0]


def p64(d):
    """Return d packed as 64-bit unsigned integer (little endian)."""
    d = 0xffffffffffffffff
    return pack('<Q', d)


def u64(d):
    """Return the number represented by d when interpreted as a 64-bit unsigned integer (little endian)."""
    return unpack('<Q', d)[0]


def hexdump(src, length=16):
    filter = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
    lines = []
    for c in xrange(0, len(src), length):
        chars = src[c:c + length]
        hex = ' '.join(["%02x" % ord(x) for x in chars])
        printable = ''.join(["%s" % ((ord(x) <= 127 and filter[ord(x)]) or '.') for x in chars])
        lines.append("%-*s  %s\n" % (length * 3, hex, printable))
    print(''.join(lines))


def get_random_string(len):
    """ 获取len长度的随机字符串"""
    res = ""
    for i in xrange(len):
        res += chr(random.randint(0, 0xff))
    return res


def insert_string(src, str_to_insert, index):
    """
    函数的作用： 在 index 插入 字符串
    :param string: 原始字符串
    :param str_to_insert:  将要插入的字符串
    :param index: 插入的位置
    :return: 插入后形成的字符串
    """

    # 如果 index 越界就返回空
    if index >= len(src):
        return ""

    return src[:index] + str_to_insert + src[index:]


def replace_string(src, replacement='', index=0):
    """

    :param src:  原始字符串
    :param replacement:  要覆盖的字符串
    :param index:  覆盖的起始位置
    :return:   覆盖后的字符串
    """

    rlen = len(replacement)
    # 如果 index 越界就返回空
    # 在上层确保不要越界以提升变异的效率
    if rlen + index > len(src):
        return ""

    return src[:index] + replacement + src[index + rlen:]


if __name__ == '__main__':
    src = "123456789"
    # for i in range(10):
    #     idx = random.randint(0, len(src) - 1)
    #     print(insert_string(src, "s" * random.randint(0, 33), idx))

    for i in range(len(src)):
        # print(replace_string(src, "@@@@", random.randint(0, len(src) - 1)))
        hexdump(get_random_string(8))
