#!/usr/bin/python
# -*- coding: UTF-8 -*-

import difflib
import random
from cpf.mutate.Mutater import Mutater
from cpf.misc.utils import hexdump
import matplotlib.pyplot as plt

INIT_SET = ["aaaaabbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbaaaaaaaaa",
            "aaaaabcccccccccccccccccccccccccccbbbaaaaa", "acccccccccccccccccccaaaaddddaaaaa"]


def fitness(raw, dirty):
    return difflib.SequenceMatcher(None, raw, dirty).quick_ratio()


def chose(q, count):  ## 输入摇号名额，参与摇号人员的ID和权重

    weight = []
    id = []
    for i in q:
        id.append(i[0])
        weight.append(i[1])

    num = len(id)
    l_weight = []
    for k in range(num):
        if k == 0:
            l_weight.append(weight[k])
        else:
            l_weight.append(l_weight[k - 1] + weight[k])  ##计算累积权重

    items = []
    for i in range(count):
        luck_num = random.uniform(0, l_weight[num - 1])  ##生成每次摇号的幸运值
        for m in range(num):
            if luck_num <= l_weight[m]:
                items.append(id[m])
                break
    return items


def cross(p1, p2):
    """
    样本交叉编译， p1 的前面部分 + p2 的后面部分
    :param p1:
    :param p2:
    :return:
    """
    ret = ""
    if len(p1) == 1:
        ret += p1
    else:
        idx1 = random.randint(1, len(p1) - 1)
        ret += p1[:idx1]

    if len(p2) == 1:
        ret += p2
    else:
        idx2 = random.randint(1, len(p2) - 1)
        ret += p2[:idx2]

    return ret


def fuzz(data):
    ret = ""
    for c in data:
        if random.random() < 0.15:
            ret += chr(random.randint(0, 255))
        else:
            ret += c

    return ret


if __name__ == '__main__':
    QUEUE = []
    mutater = Mutater(mutate_max_count=5)
    raw = random.choice(INIT_SET)
    # Y = []
    # for i in range(200):
    #     dirty = mutater.mutate(raw, fuzz_rate=0.3)
    #     score = fitness(raw, dirty)
    #     hexdump(dirty)
    #     print score
    #     Y.append(score)
    #
    # print Y
    # plt.title('Test')
    # plt.scatter(range(len(Y)), Y)
    # plt.show()
    # exit(0)

    for i in range(4):
        # dirty = mutater.mutate(raw)
        dirty = fuzz(raw)
        score = fitness(raw, dirty)
        QUEUE.append((dirty, score))
        # 由大到小排列
        QUEUE = sorted(QUEUE, key=lambda x: x[1], reverse=True)

    Y = []
    for i in range(1000):
        if random.random() < 0.4:
            p1, p2 = chose(QUEUE, 2)
            c = cross(p1, p2)  # 杂交
        else:
            c = QUEUE[0][0]
        dirty = mutater.mutate(c, fuzz_rate=0.3)
        hexdump(dirty)
        score = fitness(raw, dirty)
        QUEUE.append((dirty, score))
        QUEUE = sorted(QUEUE, key=lambda x: x[1], reverse=True)
        Y.append(score)

    print Y
    plt.title('GA')
    plt.scatter(range(len(Y)), Y)
    plt.show()

    Y = []
    for i in range(1000):
        dirty = mutater.mutate(raw, fuzz_rate=0.3)
        score = fitness(raw, dirty)
        hexdump(dirty)
        Y.append(score)

    print Y
    plt.title('NO GA')
    plt.scatter(range(len(Y)), Y)
    plt.show()
