#!/usr/bin/python
# -*- coding: UTF-8 -*-
from collections import deque
import json


class SequenceLogger:

    def __init__(self, maxlen=3):
        self.log_queue = deque(maxlen=maxlen)

    def add_to_queue(self, seqs):
        """
        增加测试序列到日志队列
        :param pre_seqs: 前序包序列
        :param fuzz_seq: 测试包数据
        :return:
        """

        self.log_queue.append(json.dumps(seqs))

    def dump_sequence(self):

        seqs = []
        while True:
            try:
                # 一般来说第一个应该就是触发异常的发包序列， 不过为了一些极个别情况，把最近的 3 次发包序列都打印出来
                seqs.append(json.loads(self.log_queue.pop()))
            except:
                break

        print json.dumps(seqs)
