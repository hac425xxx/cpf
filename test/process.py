#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import subprocess


def check_pid(pid):
    pid = str(pid)
    try:
        res = subprocess.check_output("ps -fp {}".format(pid), shell=True)
        if pid in res:
            return True
        else:
            return False
    except:
        return False


if __name__ == "__main__":
    print check_pid(12703)
