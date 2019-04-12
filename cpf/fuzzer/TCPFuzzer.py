#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from cpf.protocol.network.TCPCommunicator import TCPCommunicator
from Fuzzer import Fuzzer


class TCPFuzzer(Fuzzer):
    def __init__(self, p1, p2, nomal_trans_conf, sample_path="", logseq_count=3, interval=0.01,
                 workspace=""):
        Fuzzer.__init__(self, p1, p2, TCPCommunicator, nomal_trans_conf, sample_path, logseq_count, interval,
                        workspace)


if __name__ == '__main__':
    # fuzzer = TCPFuzzer("192.168.245.131", 21, nomal_trans_conf="/fuzzer/test/conf/floatftp", interval=0)
    fuzzer = TCPFuzzer("192.168.245.131", 21, nomal_trans_conf="/fuzzer/test/conf/floatftp", interval=0)

    fuzzer.fuzz()

    maybe_crash_seqs = [[{"recv": "50617373776f7264207265717569726564", "send": "5553455220667265650D0A"},
                         {"recv": "6c6f6767656420696e",
                          "send": "50fefefefefe206650e2bd672066729f9933b712097f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7fbd672066727f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7fbd67206672965a42670d0e50405b"}],
                        [{"recv": "50617373776f7264207265717569726564", "send": "5553455220667265650D0A"},
                         {"recv": "6c6f6767656420696e", "send": "500406504153667263ffffffffffffff19"}],
                        [{"recv": "50617373776f7264207265717569726564", "send": "5553455220667265650D0A"},
                         {"recv": "6c6f6767656420696e", "send": "50415353203e5050df504109160492e43f1b"}]]
    for seq in maybe_crash_seqs:
        if fuzzer.check_vuln(seq):
            print json.dumps(seq)
            exit(0)
