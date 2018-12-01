#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from time import sleep
from collections import deque
from cpf.mutate.Mutater import Mutater
from cpf.protocol.network.TCPCommunicator import TCPCommunicator

mutater = Mutater()
trans_data = {}

test_count = 100

with open("data/float_ftp.json", "r") as fp:
    trans_data = json.loads(fp.read())

end_stats = trans_data["end_states"]
welcome_msg = trans_data["welcome_msg"].decode("hex")
trans = trans_data["trans"]

q = deque(maxlen=3)


def generate_prepare(trans, idx):
    """
    生成到到待测状态需要的前序包
    :param trans: 所有的 trans 字典
    :param idx: 待测状态的索引
    :return:
    """
    seqs = []
    seq = {}
    for i in xrange(idx):
        seq = {}
        seq['send'] = trans[i]['send']
        seq['recv'] = trans[i]['recv']
        seqs.append(seq)
    return seqs


def dump_seq(pre_seqs, seq):
    for s in pre_seqs:
        print("send: {}".format(s['send']))
    print("send: {}".format(seq['send']))


def dump_testseq(seq):
    for s in seq:
        print("send: {}".format(s['send']))


count = 0

factor = 6


def add_to_queue(pre_seqs, fuzz_seq):
    global q
    test_seq = []
    test_seq += pre_seqs
    test_seq.append(fuzz_seq)
    q.append(test_seq)


def send(pre_seqs, fuzz_seq):
    """
    按照包的序列发包
    :param pre_seqs: 交互序列，一个数组，每一项表示 发包和接收包的数据
    :param fuzz_seq: 利用变异引擎生成的变异包。
    :return:
    """
    global count
    count += 1
    print("fuzz count: {}".format(count))

    p = ""

    # 尝试连接服务器
    retry = 0
    while retry < 3:
        try:
            p = TCPCommunicator("192.168.245.135", 21)
            break
        except:
            retry += 1
            sleep(0.2)

    if retry == 3:
        print("retry done!!!")
        return

    # 获取欢迎消息
    recv = p.recv(1024)
    while welcome_msg not in recv:
        recv = p.recv(1024)

    # 发送前序数据包序列
    for seq in pre_seqs:
        p.send(seq['send'].decode('hex'))
        recv = p.recv(1024)
        if seq['recv'].decode('hex') not in recv:
            print("@{}@----@{}@".format(seq['recv'].decode('hex'), recv))

    # 发送 fuzz 数据包
    p.send(fuzz_seq['send'].decode('hex'))

    # 关闭连接
    del p

    # 重新连接服务器，判断是否存活
    print("check live for {}".format(count))
    p = TCPCommunicator("192.168.245.135", 21)

    recv = p.recv(1024)
    if welcome_msg not in recv:
        print recv
        print("die")
        raise Exception("server is seen die!!")
    del p


def fuzzall():
    """
    fuzz 所有的状态
    :return:
    """
    global mutater, factor
    while True:

        # 遍历整个 trans
        for i in xrange(len(trans)):

            print("inc factor")
            factor += 1
            mutater = Mutater(factor)

            print("state:" + trans[i]['state'])

            init_case = trans[i]['send'].decode("hex")

            # 到达生成当前状态的前序数据包
            pre_seqs = generate_prepare(trans, i)

            # 更加 test_count 觉定在当前状态的 fuzz 次数
            for c in xrange(test_count):
                # 生成变异后的数据包
                fuzz_seq = {}
                fuzz_seq['send'] = mutater.mutate(init_case).encode("hex")
                fuzz_seq['recv'] = trans[i]['recv']

                try:

                    #  发送数据包序列前，把当前要发送序列存入 最大长度为 3 的队列里面， 用于后续记录日志
                    add_to_queue(pre_seqs, fuzz_seq)
                    send(pre_seqs, fuzz_seq)
                except Exception as e:
                    print e

                    # 服务以及挂了，打印测试序列
                    while True:
                        try:
                            # 一般来说第一个应该就是触发异常的发包序列， 不过为了一些极个别情况，把最近的 3 次发包序列都打印出来
                            test_seq = q.pop()
                            print "*" * 20
                            print json.dumps(test_seq)
                        except:
                            break
                    exit(0)


def fuzz(idx):
    """
    fuzz 指定的一个状态 idx
    :param idx:
    :return:
    """
    global mutater, factor

    while True:

        print("inc factor")
        factor += 1
        mutater = Mutater(factor)

        print("state:" + trans[idx]['state'])
        init_case = trans[idx]['send'].decode("hex")

        # 到达生成当前状态的前序数据包
        pre_seqs = generate_prepare(trans, idx)

        # 更加 test_count 觉定在当前状态的 fuzz 次数
        for c in xrange(test_count):
            # 生成变异后的数据包
            fuzz_seq = {}
            fuzz_seq['send'] = mutater.mutate(init_case).encode("hex")
            fuzz_seq['recv'] = trans[idx]['recv']

            try:
                send(pre_seqs, fuzz_seq)
            except Exception as e:
                print e
                dump_seq(pre_seqs, fuzz_seq)
                exit(0)


if __name__ == '__main__':
    fuzzall()
    # fuzz(2)
