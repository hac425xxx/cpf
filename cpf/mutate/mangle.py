#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: mangle.py
@time: 2018/11/3 18:50
@desc: 实现各种变异函数
"""
import random
from utils import *


def mangle_resize(data):
    """
    随机插入 若干个 空格到  data 里面
    :param data:
    :return:
    """
    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(0, length)
    # 获取插入位置, length - size 确保不会越界
    idx = random.randint(0, length - size)

    return replace_string(data, " " * size, idx)


def mangle_byte(data):
    """
    往随机位置写随机 一字节数据
    """
    data = list(data)
    length = len(data)
    off = random.randint(0, length - 1)
    data[off] = chr(random.randint(0, 0xff))
    return "".join(data)


def mangle_bit(data):
    """
    取随机位置的数值做位翻转
    """
    data = list(data)
    length = len(data)
    off = random.randint(0, length - 1)

    # 从随机位置取出一个字节，后续来做位翻转
    byte = ord(data[off])

    # 从 byte 中随机取一位做 位翻转 ， 利用  1 和异或的特性
    data[off] = chr(byte ^ (1 << random.randint(0, 7)))
    return "".join(data)


def mangle_bytes(data):
    """
    在随机位置覆盖写2~4字节数据
    """

    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(2, 4)

    # 获取插入位置, length - size 确保不会越界
    idx = random.randint(0, length - size)
    #  获取 size 长的随机字符串， 然后复写到指定位置
    return replace_string(data, get_random_string(size), idx)


def mangle_magic(data):
    """
    对随机位置的字符串采用 边界值来替换
    """

    # 里面包含了各种边界值， 1, 2, 4, 8 字节， 供程序选择
    magic_string = [
        #  1 字节 的数据
        "\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07", "\x08", "\x09", "\x0A", "\x0B", "\x0C",
        "\x0D", "\x0E", "\x0F", "\x10", "\x20", "\x40", "\x7E", "\x7F", "\x80", "\x81", "\xC0", "\xFE", "\xFF",

        #  2 字节的数据
        "\x00\x00", "\x01\x01", "\x80\x80", "\xFF\xFF", "\x00\x01", "\x00\x02", "\x00\x03", "\x00\x04",
        "\x00\x05", "\x00\x06", "\x00\x07", "\x00\x08", "\x00\x09", "\x00\x0A", "\x00\x0B", "\x00\x0C",
        "\x00\x0D", "\x00\x0E", "\x00\x0F", "\x00\x10", "\x00\x20", "\x00\x40", "\x00\x7E", "\x00\x7F",
        "\x00\x80", "\x00\x81", "\x00\xC0", "\x00\xFE", "\x00\xFF", "\x7E\xFF", "\x7F\xFF", "\x80\x00",
        "\x80\x01", "\xFF\xFE", "\x00\x00", "\x01\x00", "\x02\x00", "\x03\x00", "\x04\x00", "\x05\x00",
        "\x06\x00", "\x07\x00", "\x08\x00", "\x09\x00", "\x0A\x00", "\x0B\x00", "\x0C\x00", "\x0D\x00",
        "\x0E\x00", "\x0F\x00", "\x10\x00", "\x20\x00", "\x40\x00", "\x7E\x00", "\x7F\x00", "\x80\x00",
        "\x81\x00", "\xC0\x00", "\xFE\x00", "\xFF\x00", "\xFF\x7E", "\xFF\x7F", "\x00\x80", "\x01\x80",
        "\xFE\xFF",

        # 4 字节
        "\x00\x00\x00\x00", "\x01\x01\x01\x01", "\x80\x80\x80\x80", "\xFF\xFF\xFF\xFF",
        "\x00\x00\x00\x01", "\x00\x00\x00\x02", "\x00\x00\x00\x03", "\x00\x00\x00\x04", "\x00\x00\x00\x05",
        "\x00\x00\x00\x06", "\x00\x00\x00\x07", "\x00\x00\x00\x08", "\x00\x00\x00\x09", "\x00\x00\x00\x0A",
        "\x00\x00\x00\x0B", "\x00\x00\x00\x0C", "\x00\x00\x00\x0D", "\x00\x00\x00\x0E", "\x00\x00\x00\x0F",
        "\x00\x00\x00\x10", "\x00\x00\x00\x20", "\x00\x00\x00\x40", "\x00\x00\x00\x7E", "\x00\x00\x00\x7F",
        "\x00\x00\x00\x80", "\x00\x00\x00\x81", "\x00\x00\x00\xC0", "\x00\x00\x00\xFE", "\x00\x00\x00\xFF",
        "\x7E\xFF\xFF\xFF", "\x7F\xFF\xFF\xFF", "\x80\x00\x00\x00", "\x80\x00\x00\x01", "\xFF\xFF\xFF\xFE",
        "\x00\x00\x00\x00", "\x01\x00\x00\x00", "\x02\x00\x00\x00", "\x03\x00\x00\x00", "\x04\x00\x00\x00",
        "\x05\x00\x00\x00", "\x06\x00\x00\x00", "\x07\x00\x00\x00", "\x08\x00\x00\x00", "\x09\x00\x00\x00",
        "\x0A\x00\x00\x00", "\x0B\x00\x00\x00", "\x0C\x00\x00\x00", "\x0D\x00\x00\x00", "\x0E\x00\x00\x00",
        "\x0F\x00\x00\x00", "\x10\x00\x00\x00", "\x20\x00\x00\x00", "\x40\x00\x00\x00", "\x7E\x00\x00\x00",
        "\x7F\x00\x00\x00", "\x80\x00\x00\x00", "\x81\x00\x00\x00", "\xC0\x00\x00\x00", "\xFE\x00\x00\x00",
        "\xFF\x00\x00\x00", "\xFF\xFF\xFF\x7E", "\xFF\xFF\xFF\x7F", "\x00\x00\x00\x80", "\x01\x00\x00\x80",
        "\xFE\xFF\xFF\xFF",

        # 8 字节
        "\x00\x00\x00\x00\x00\x00\x00\x00", "\x01\x01\x01\x01\x01\x01\x01\x01",
        "\x80\x80\x80\x80\x80\x80\x80\x80", "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF",
        "\x00\x00\x00\x00\x00\x00\x00\x01", "\x00\x00\x00\x00\x00\x00\x00\x02",
        "\x00\x00\x00\x00\x00\x00\x00\x03", "\x00\x00\x00\x00\x00\x00\x00\x04",
        "\x00\x00\x00\x00\x00\x00\x00\x05", "\x00\x00\x00\x00\x00\x00\x00\x06",
        "\x00\x00\x00\x00\x00\x00\x00\x07", "\x00\x00\x00\x00\x00\x00\x00\x08",
        "\x00\x00\x00\x00\x00\x00\x00\x09", "\x00\x00\x00\x00\x00\x00\x00\x0A",
        "\x00\x00\x00\x00\x00\x00\x00\x0B", "\x00\x00\x00\x00\x00\x00\x00\x0C",
        "\x00\x00\x00\x00\x00\x00\x00\x0D", "\x00\x00\x00\x00\x00\x00\x00\x0E",
        "\x00\x00\x00\x00\x00\x00\x00\x0F", "\x00\x00\x00\x00\x00\x00\x00\x10",
        "\x00\x00\x00\x00\x00\x00\x00\x20", "\x00\x00\x00\x00\x00\x00\x00\x40",
        "\x00\x00\x00\x00\x00\x00\x00\x7E", "\x00\x00\x00\x00\x00\x00\x00\x7F",
        "\x00\x00\x00\x00\x00\x00\x00\x80", "\x00\x00\x00\x00\x00\x00\x00\x81",
        "\x00\x00\x00\x00\x00\x00\x00\xC0", "\x00\x00\x00\x00\x00\x00\x00\xFE",
        "\x00\x00\x00\x00\x00\x00\x00\xFF", "\x7E\xFF\xFF\xFF\xFF\xFF\xFF\xFF",
        "\x7F\xFF\xFF\xFF\xFF\xFF\xFF\xFF", "\x80\x00\x00\x00\x00\x00\x00\x00",
        "\x80\x00\x00\x00\x00\x00\x00\x01", "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFE",
        "\x00\x00\x00\x00\x00\x00\x00\x00", "\x01\x00\x00\x00\x00\x00\x00\x00",
        "\x02\x00\x00\x00\x00\x00\x00\x00", "\x03\x00\x00\x00\x00\x00\x00\x00",
        "\x04\x00\x00\x00\x00\x00\x00\x00", "\x05\x00\x00\x00\x00\x00\x00\x00",
        "\x06\x00\x00\x00\x00\x00\x00\x00", "\x07\x00\x00\x00\x00\x00\x00\x00",
        "\x08\x00\x00\x00\x00\x00\x00\x00", "\x09\x00\x00\x00\x00\x00\x00\x00",
        "\x0A\x00\x00\x00\x00\x00\x00\x00", "\x0B\x00\x00\x00\x00\x00\x00\x00",
        "\x0C\x00\x00\x00\x00\x00\x00\x00", "\x0D\x00\x00\x00\x00\x00\x00\x00",
        "\x0E\x00\x00\x00\x00\x00\x00\x00", "\x0F\x00\x00\x00\x00\x00\x00\x00",
        "\x10\x00\x00\x00\x00\x00\x00\x00", "\x20\x00\x00\x00\x00\x00\x00\x00",
        "\x40\x00\x00\x00\x00\x00\x00\x00", "\x7E\x00\x00\x00\x00\x00\x00\x00",
        "\x7F\x00\x00\x00\x00\x00\x00\x00", "\x80\x00\x00\x00\x00\x00\x00\x00",
        "\x81\x00\x00\x00\x00\x00\x00\x00", "\xC0\x00\x00\x00\x00\x00\x00\x00",
        "\xFE\x00\x00\x00\x00\x00\x00\x00", "\xFF\x00\x00\x00\x00\x00\x00\x00",
        "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7E", "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F",
        "\x00\x00\x00\x00\x00\x00\x00\x80", "\x01\x00\x00\x00\x00\x00\x00\x80",
        "\xFE\xFF\xFF\xFF\xFF\xFF\xFF\xFF"
    ]

    length = len(data)
    # 选择一个 magic_string 插入
    midx = random.randint(0, len(magic_string) - 1)
    mlen = len(magic_string[midx])

    #  如果 选中的 magic_string 的长度大于 data 的长度就不变异了
    if mlen >= length:
        return data

    # 获取插入位置, length - mlen 确保不会越界
    idx = random.randint(0, length - mlen)
    #  获取 magic_string , 然后插入进去
    return replace_string(data, magic_string[midx], idx)


def mangle_incbyte(data):
    """
    取随机位置的数值 加 1
    """
    data = list(data)
    length = len(data)
    off = random.randint(0, length - 1)

    # 随机取出字符，然后加1
    data[off] = chr(ord(data[off]) + 1)
    return "".join(data)


def mangle_decbyte(data):
    """
    取随机位置的数值 减 1
    """
    data = list(data)
    length = len(data)
    off = random.randint(0, length - 1)

    # 随机取出字符，然后减1
    data[off] = chr(ord(data[off]) - 1)
    return "".join(data)


def mangle_negbyte(data):
    """
    取随机位置的数值 取反
    """
    data = list(data)
    length = len(data)
    off = random.randint(0, length - 1)

    # 随机取出字符，然后取反， 注意只要最低 8 字节
    data[off] = chr((~ord(data[off])) & 0xff)
    return "".join(data)


def mangle_add_sub(data):
    """
    取随机位置的1 , 2, 4 或者8 字节做加减操作
    """

    length = len(data)
    #  选择变量长度
    var_len = 1 << random.randint(0, 3)
    off = random.randint(0, length - var_len)

    # 操作数
    delta = random.randint(0, 8192) - 4096

    if var_len == 1:
        c = u8(data[off: off + var_len])
        if delta & 1:
            c = c + delta
        else:
            c = c - delta
        data = replace_string(data, p8(c), off)
    elif var_len == 2:
        c = u16(data[off: off + var_len])
        if delta & 1:
            c = c + delta
        else:
            c = c - delta

        data = replace_string(data, p16(c), off)

    elif var_len == 4:
        c = u32(data[off: off + var_len])
        if delta & 1:
            c = c + delta
        else:
            c = c - delta

        data = replace_string(data, p32(c), off)

    else:
        c = u64(data[off: off + var_len])
        if delta & 1:
            c = c + delta
        else:
            c = c - delta
        data = replace_string(data, p64(c), off)

    return data


def mangle_mem_copy(data):
    """
    取随机位置， 随机长度的数据，复制到随机位置， 覆盖
    """

    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(0, length - 1)

    off_from = random.randint(0, length - size)
    off_to = random.randint(0, length - size)

    return replace_string(data, data[off_from:off_from + size], off_to)


def mangle_mem_insert(data):
    """
    取随机位置， 随机长度的数据，插入到随机位置
    """

    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(0, length - 1)

    off_from = random.randint(0, length - size)
    off_to = random.randint(0, length - 1)

    return insert_string(data, data[off_from:off_from + size], off_to)


def mangle_memset_max(data):
    """  在随机位置填充随机长度的 特殊字符， 0xff, 0x7f ....... """
    # https://security.tencent.com/index.php/blog/msg/35
    special_char = ['\x00', '\xFF', '\x3F', '\x7F', '\x80', '\xFE', '\x60']
    byte = special_char[random.randint(0, len(special_char) - 1)]
    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(0, length - 1)
    off = random.randint(0, length - size)
    return replace_string(data, byte * size, off)


def mangle_random(data):
    """  取随机位置、随机大小的缓冲区，用随机数填充 """

    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(0, length - 1)
    off = random.randint(0, length - size)
    return replace_string(data, get_random_string(size), off)


def mangle_clonebyte(data):
    """
    取两处随机位置的作数据交换
    """

    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(0, length - 1)

    off_from = random.randint(0, length - size)
    data_from = data[off_from:off_from + size]

    off_to = random.randint(0, length - size)
    data_to = data[off_to:off_to + size]
    data = replace_string(data, data_from, off_to)
    data = replace_string(data, data_to, off_from)
    return data


def mangle_expand(data):
    """
    在随机位置，取随机长度的数据追加到数据末尾
    """

    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(0, length - 1)
    off = random.randint(0, length - size)

    return data + data[off:off + size]


def mangle_shrink(data):
    """
    随机删减内容
    """

    length = len(data)
    # 获取要填充的数据的长度
    size = random.randint(0, length - 1)
    off = random.randint(0, length - size)
    return data[:off] + data[off + size + 1:]


def mangle_insert_rnd(data):
    """  在随机位置插入随机长度(长度最大为文件自身长度)的字符串 """

    length = len(data)
    # 获取要填充的数据的长度
    off = random.randint(0, length - 1)
    size = random.randint(0, len(data))
    return insert_string(data, get_random_string(size), off)


if __name__ == '__main__':
    src = "123456789"

    for i in range(20):
        # print(mangle_resize(src))
        # hexdump(mangle_byte(src))
        # hexdump(mangle_bit(src))
        # hexdump(mangle_bytes(src))
        # hexdump(mangle_magic(src))
        # hexdump(mangle_incbyte(src))
        # hexdump(mangle_decbyte(src))
        # hexdump(mangle_negbyte(src))
        # hexdump(mangle_add_sub(src))
        # hexdump(mangle_mem_copy(src))
        # hexdump(mangle_mem_insert(src))
        # hexdump(mangle_memset_max(src))
        # hexdump(mangle_random(src))
        # hexdump(mangle_clonebyte(src))
        # hexdump(mangle_expand(src))
        # hexdump(mangle_shrink(src))
        hexdump(mangle_insert_rnd(src))
