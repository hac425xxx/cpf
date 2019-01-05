#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import os


def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


if __name__ == "__main__":
    # print check_pid(94133)
    task_id = "sssssssssssssssssssss"
    cmd = "ps -ef | grep python | grep %s | awk  '{print $2}' |xargs  kill -9" % (task_id)
    print cmd
