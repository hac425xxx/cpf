#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pwn import *

# context.log_level = "debug"
p = remote("192.168.245.131", 21)

p.send("USER free\r\n")

print p.recvuntil("331")
p.send("PASS frx\r\n")

print p.recvuntil("230")

p.send("PWD\r\n")

print p.recv(1024)
