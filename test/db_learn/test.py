#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import uuid

# for i in range(10):
#     print uuid.uuid1()
#
# exit(0)

conn = sqlite3.connect("/tmp/test.db")
cursor = conn.cursor()

cursor.execute('create table if not exists user (id varchar(20) primary key, name varchar(20))')
cursor.execute("insert into user (id, name) values ('{}', 'Michael')".format(uuid.uuid1()))

cursor.close()
conn.commit()

users = conn.execute("select * from user")

for user in users:
    print user

conn.close()
