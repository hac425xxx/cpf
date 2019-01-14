#!/usr/bin/python
# -*- coding: UTF-8 -*-
from collections import deque
import json
import os
import datetime
from queue import Queue
from threading import Thread

LOG_QUEUE = Queue()


def save_log(base):
    print "\n日志保存目录：{}\n".format(base)
    count = 1
    while True:
        seqs = LOG_QUEUE.get()
        path = os.path.join(base, "{}.json".format(count))
        count += 1
        with open(path, "w") as fp:
            fp.write(seqs)


class SequenceLogger:

    def __init__(self, maxlen=5, log_dir=""):
        """

        :param maxlen:  最多保存的序列个数
        :param log_dir:    日志保存位置
        """
        self.log_queue = []

        if log_dir == "":
            # 默认日志保存在 fuzz.py 目录下
            file_dir = os.path.dirname(__file__)
            self.log_dir = os.path.abspath(os.path.join(file_dir, "../../logs"))
        else:
            self.log_dir = log_dir

        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        self.save_thread = Thread(target=save_log, args=(self.log_dir,))
        self.save_thread.start()

    def add_to_queue(self, seqs):
        """
        增加测试序列到日志队列
        :param pre_seqs: 前序包序列
        :param fuzz_seq: 测试包数据
        :return:
        """

        self.log_queue.append(json.dumps(seqs))

        if len(self.log_queue) > 100:
            self.put_seqs_to_thread()

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
        with open(os.path.join(self.log_dir, self.get_log_filename()), "w") as fp:
            fp.write(json.dumps(seqs))
        return seqs

    def get_log_filename(self):
        i = datetime.datetime.now()
        filename = "{}_{:02d}_{:02d}_{:02d}_{:02d}_{:02d}.log".format(i.year, i.month, i.day, i.hour, i.minute,
                                                                      i.second)
        return filename

    def put_seqs_to_thread(self):
        seqs = []
        while True:
            try:
                # 把日志队列里面的序列取出保存
                seqs.append(json.loads(self.log_queue.pop()))
            except:
                break

        LOG_QUEUE.put(json.dumps(seqs))


if __name__ == '__main__':
    logger = SequenceLogger()
    logger.add_to_queue([1, 2, 4])
    logger.add_to_queue([2, 3, 4])
    print logger.dump_sequence()
    print logger.log_dir
