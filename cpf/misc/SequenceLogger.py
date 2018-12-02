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

        self.log_queue.append(seqs)

    def dump_sequence(self):
        # 服务以及挂了，打印测试序列
        while True:
            try:
                # 一般来说第一个应该就是触发异常的发包序列， 不过为了一些极个别情况，把最近的 3 次发包序列都打印出来
                test_seq = self.log_queue.pop()
                print "*" * 20
                print json.dumps(test_seq)
            except:
                break
