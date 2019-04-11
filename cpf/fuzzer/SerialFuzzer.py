#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from time import sleep
from cpf.mutate.Mutater import Mutater
from cpf.misc.utils import *
from cpf.misc.SequenceLogger import SequenceLogger
from cpf.protocol.serial.Serial import Serial
from Fuzzer import Fuzzer
import random, os


class SerialFuzzer(Fuzzer):
    def __init__(self, p1, p2, nomal_trans_conf, sample_path="", logseq_count=3, interval=0.01, workspace=""):
        Fuzzer.__init__(self, p1, p2, Serial, nomal_trans_conf, sample_path, logseq_count, interval,
                        workspace)


if __name__ == '__main__':
    fuzzer = SerialFuzzer("/dev/ttyS0", 115200,
                          nomal_trans_conf="../../test/conf/serial_test.json")

    fuzzer.fuzz()

    maybe_crash_seqs = [[{"recv": "bbccdd", "send": "aabbccdd20e5f8ffbaccdd"}],
                        [{"recv": "bbccdd", "send": "ccb3ccff009b"}],
                        [{"recv": "bbccdd", "send": "ab"}]]
    for seq in maybe_crash_seqs:
        if fuzzer.check_vuln(seq):
            print json.dumps(seq)
            exit(0)
