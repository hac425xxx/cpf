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
                # 把日志队列里面的序列取出保存
                seqs.append(json.loads(self.log_queue.pop()))
            except:
                break

        #  seqs 的第一项应该是触发异常的用例
        # print json.dumps(seqs)
        return seqs
