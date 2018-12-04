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
import socket
import scapy.all as scapy
from time import sleep
import os

CHAR_LIST = ["\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07", "\x08", "\x09", "\x0a", "\x0b", "\x0c",
             "\x0d", "\x0e", "\x0f", "\x10", "\x11", "\x12", "\x13", "\x14", "\x15", "\x16", "\x17", "\x18", "\x19",
             "\x1a", "\x1b", "\x1c", "\x1d", "\x1e", "\x1f", "\x20", "\x21", "\x22", "\x23", "\x24", "\x25", "\x26",
             "\x27", "\x28", "\x29", "\x2a", "\x2b", "\x2c", "\x2d", "\x2e", "\x2f", "\x30", "\x31", "\x32", "\x33",
             "\x34", "\x35", "\x36", "\x37", "\x38", "\x39", "\x3a", "\x3b", "\x3c", "\x3d", "\x3e", "\x3f", "\x40",
             "\x41", "\x42", "\x43", "\x44", "\x45", "\x46", "\x47", "\x48", "\x49", "\x4a", "\x4b", "\x4c", "\x4d",
             "\x4e", "\x4f", "\x50", "\x51", "\x52", "\x53", "\x54", "\x55", "\x56", "\x57", "\x58", "\x59", "\x5a",
             "\x5b", "\x5c", "\x5d", "\x5e", "\x5f", "\x60", "\x61", "\x62", "\x63", "\x64", "\x65", "\x66", "\x67",
             "\x68", "\x69", "\x6a", "\x6b", "\x6c", "\x6d", "\x6e", "\x6f", "\x70", "\x71", "\x72", "\x73", "\x74",
             "\x75", "\x76", "\x77", "\x78", "\x79", "\x7a", "\x7b", "\x7c", "\x7d", "\x7e", "\x7f", "\x80", "\x81",
             "\x82", "\x83", "\x84", "\x85", "\x86", "\x87", "\x88", "\x89", "\x8a", "\x8b", "\x8c", "\x8d", "\x8e",
             "\x8f", "\x90", "\x91", "\x92", "\x93", "\x94", "\x95", "\x96", "\x97", "\x98", "\x99", "\x9a", "\x9b",
             "\x9c", "\x9d", "\x9e", "\x9f", "\xa0", "\xa1", "\xa2", "\xa3", "\xa4", "\xa5", "\xa6", "\xa7", "\xa8",
             "\xa9", "\xaa", "\xab", "\xac", "\xad", "\xae", "\xaf", "\xb0", "\xb1", "\xb2", "\xb3", "\xb4", "\xb5",
             "\xb6", "\xb7", "\xb8", "\xb9", "\xba", "\xbb", "\xbc", "\xbd", "\xbe", "\xbf", "\xc0", "\xc1", "\xc2",
             "\xc3", "\xc4", "\xc5", "\xc6", "\xc7", "\xc8", "\xc9", "\xca", "\xcb", "\xcc", "\xcd", "\xce", "\xcf",
             "\xd0", "\xd1", "\xd2", "\xd3", "\xd4", "\xd5", "\xd6", "\xd7", "\xd8", "\xd9", "\xda", "\xdb", "\xdc",
             "\xdd", "\xde", "\xdf", "\xe0", "\xe1", "\xe2", "\xe3", "\xe4", "\xe5", "\xe6", "\xe7", "\xe8", "\xe9",
             "\xea", "\xeb", "\xec", "\xed", "\xee", "\xef", "\xf0", "\xf1", "\xf2", "\xf3", "\xf4", "\xf5", "\xf6",
             "\xf7", "\xf8", "\xf9", "\xfa", "\xfb", "\xfc", "\xfd", "\xfe", "\xff"]


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
        res += random.choice(CHAR_LIST)
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
    if index > len(src):
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


def generate_preseqs(trans, idx):
    """
    利用 trans 生成到待测状态 idx, 需要的前序包
    :param trans: 所有的 trans 字典
    :param idx: 待测状态的索引
    :return:[{"send":"xxx", "recv":"kkkk"}]
    """
    seqs = []
    for i in xrange(idx):
        seq = {}
        seq['send'] = trans[i]['send']
        seq['recv'] = trans[i]['recv']
        seqs.append(seq)
    return seqs


def check_tcp_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    if result == 0:
        return True
    else:
        return False


def check_udp_port(host, port):
    ''' send to /dev/null 2>&1 to suppress terminal output '''
    res = os.system("nc -vnzu {} {} > /dev/null 2>&1".format(host, port))
    if res == 0:
        return True
    else:
        return False


def check_udp_port_by_recv(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        sock.sendto('hx', (host, port))
        sock.recvfrom(1024)
        return True
    except:
        return False


if __name__ == '__main__':
    src = "123456789"
    # for i in range(10):
    #     idx = random.randint(0, len(src) - 1)
    #     print(insert_string(src, "s" * random.randint(0, 33), idx))

    # for i in range(len(src)):
    #     # print(replace_string(src, "@@@@", random.randint(0, len(src) - 1)))
    #     hexdump(get_random_string(299))

    print check_udp_port("192.168.245.135", 9999)
