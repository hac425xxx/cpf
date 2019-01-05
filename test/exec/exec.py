#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
from time import sleep

reload(sys)
sys.setdefaultencoding('utf8')

import subprocess, threading


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.thread = None

    def run(self):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()

        self.thread = threading.Thread(target=target)

        self.thread.start()

        while not self.process:
            sleep(0.1)
        return self.process.pid


def execute(cmd, cwd):
    process = subprocess.Popen(cmd, shell=True, cwd=cwd)
    process.communicate()


# thread = threading.Thread(target=execute, args=(
#     "python -u fuzz.py tcpfuzzer --host 192.168.245.131 --port 21 --conf /fuzzer/test/conf/floatftp --interval 0",
#     "/fuzzer"))
# thread.start()
#
# thread.join()

command = Command("echo 'Process started'; sleep 200; echo 'Process finished'")
print command.run()
print command

sleep(5)
if command.thread.is_alive():
    command.process.terminate()

raw_input("wait")
