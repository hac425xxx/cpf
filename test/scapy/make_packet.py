#!/usr/bin/python
# -*- coding: UTF-8 -*-

from scapy.fields import *
from scapy.packet import Packet, fuzz, Raw
from cpf.misc.utils import hexdump


class Foo(Packet):
    fields_desc = [
        ByteField("type", 0xff),
        StrFixedLenField("sep", "\xaa\xbb", 2)
    ]

    def post_build(self, p, pay):
        l = len(pay)
        p = p[:1] + hex(l)[2:] + p[2:]
        return p + pay


if __name__ == '__main__':
    p = Foo() / Raw("X" * 32)
    hexdump(str(fuzz(p)))
