#!/usr/bin/python
# -*- coding: UTF-8 -*-

from cpf.protocol.network.UDPCommunicator import UDPCommunicator
from cpf.misc.utils import *

if __name__ == '__main__':
    data = "3040020103300f02030091c8020205dc040104020103041530130400020100020100040561646d696e04000400301304000400a00d02030091c80201000201003000".decode(
        "hex")

    udp = UDPCommunicator("127.0.0.1", 1111)

    udp.send(data)

    print udp.recv(1024).encode('hex')
    # hexdump(udp.recv(1024))
