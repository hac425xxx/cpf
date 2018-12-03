#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 获取列表的第二个元素
def sort_item(elem):
    return elem['hit']


# 列表
l = [{"name": "1.png", "content": "xxxxx", "hit": 12}, {"name": "2.png", "content": "dddddddd", "hit": 23},
     {"name": "2.png", "content": "dddddddd", "hit": 3}]

# 指定第二个元素排序
l.sort(key=sort_item, reverse=True)

# 输出类别
print '排序列表：', l

command = """
ABOR
ACCT
ADAT
ALLO
APPE
AUTH
CCC	
CDUP
CONF
CWD	
DELE
ENC	
EPRT
EPSV
FEAT
HELP
LANG
LIST
LPRT
LPSV
MDTM
MIC	
MKD	
MLSD
MLST
MODE
NLST
NOOP
OPTS
PASS
PASV
PBSZ
PORT
PROT
PWD	
QUIT
REIN
REST
RETR
RMD	
RNFR
RNTO
SITE
SIZE
SMNT
STAT
STOR
STOU
STRU
SYST
TYPE
USER
XCUP
XMKD
XPWD
XRCP
XRMD
XRSQ
XSEM
XSEN
"""

tokens = []
for l in command.split("\n"):
    if l.strip():
        token = {
            "type": "plain",
            "value": l.strip() + " "
        }
        tokens.append(token)

import json

print json.dumps(tokens)
