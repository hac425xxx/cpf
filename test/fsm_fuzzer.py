#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from cpf.mutate.Mutater import Mutater

mutater = Mutater()
trans_data = {}

test_count = 4

with open("data/trans.json", "r") as fp:
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


count = 0
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
    for seq in pre_seqs:
        print("send: {}".format(seq['send'].decode('hex')))
        print("recv: {}".format(seq['recv'].decode('hex')))

    print("send: {}".format(fuzz_seq['send']))
    print("recv: {}".format(fuzz_seq['recv']))


# 遍历整个 trans
for i in xrange(len(trans)):

    print("state:" + trans[i]['state'])

    init_case = trans[i]['send'].decode("hex")

    # 到达生成当前状态的前序数据包
    seqs = generate_prepare(trans, i)

    # 更加 test_count 觉定在当前状态的 fuzz 次数
    for c in xrange(test_count):
        # 生成变异后的数据包
        seq = {}
        seq['send'] = mutater.mutate(init_case).encode("hex")
        seq['recv'] = trans[i]['recv']

        # 发包
        send(seqs, seq)
