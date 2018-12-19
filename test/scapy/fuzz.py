#!/usr/bin/python
# -*- coding: UTF-8 -*-
from scapy.fields import *
from scapy.packet import fuzz
from scapy.packet import Packet


class APDU(Packet):
    name = "APDU "
    fields_desc = [XByteField("CLA", 0),
                   XByteField("INS", 0x20),
                   XByteField("P1", 0),
                   XByteField("P2", 0),
                   ByteField("L", None)]

    def post_build(self, p, pay):
        if self.L is None:
            p = p[:4] + struct.pack("b", len(pay)) + p[5:]
        return p + pay


if __name__ == '__main__':
    from cpf.misc.utils import hexdump

    for i in range(6):
        hexdump(str(fuzz(APDU(INS=0x80, CLA=0x88))))
