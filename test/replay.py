#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
from cpf.protocol.network.TCPCommunicator import TCPCommunicator

seqs = None

with open("conf/pcman_crash.json") as fp:
    seqs = json.loads(fp.read())

p = TCPCommunicator("192.168.245.131", 21)

p.recv(1024)

for seq in seqs:
    p.send(seq['send'].decode("hex"))
    recv = p.recv(1024)
    if seq['recv'] not in recv:
        print recv

del p


p = TCPCommunicator("192.168.245.131", 21)
p.recv(1024)

del p