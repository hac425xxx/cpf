#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from time import sleep
from cpf.mutate.Mutater import Mutater
from cpf.protocol.network.TCPCommunicator import TCPCommunicator

mutater = Mutater()
trans_data = {}

test_count = 100

with open("data/float_ftp.json", "r") as fp:
    trans_data = json.loads(fp.read())

end_stats = trans_data["end_states"]
trans = trans_data["trans"]


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


count = 0

factor = 6


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

    p = TCPCommunicator("192.168.245.131", 21)

    for seq in pre_seqs:
        p.send(seq['send'].decode('hex'))
        p.recv(1)

    p.send(fuzz_seq['send'].decode('hex'))

    del p

    p = TCPCommunicator("192.168.245.131", 21)
    del p


while True:

    if count % 200 == 0:
        print("inc factor")
        factor += 1
        mutater = Mutater(factor)

    # 遍历整个 trans
    for i in xrange(len(trans)):

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
                send(pre_seqs, fuzz_seq)
            except Exception as e:
                print e
                dump_seq(pre_seqs, fuzz_seq)
                exit(0)
