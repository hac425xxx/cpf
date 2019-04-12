#!/usr/bin/python
# -*- coding: UTF-8 -*-
from cpf.protocol.network.UDPCommunicator import UDPCommunicator
from Fuzzer import Fuzzer


class UDPFuzzer(Fuzzer):
    def __init__(self, p1, p2, nomal_trans_conf, sample_path="", logseq_count=3, interval=0.01, workspace=""):
        Fuzzer.__init__(self, p1, p2, UDPCommunicator, nomal_trans_conf, sample_path, logseq_count, interval,
                        workspace)


if __name__ == '__main__':
    """
    执行命令
    net-snmp-5.7.3/agent/snmpd -f -V -c ../../snmpd.conf -Ln  127.0.0.1:1111
    """
    #
    # fuzzer = UDPFuzzer("127.0.0.1", 1111, sample_path="../../test/sample/snmp/",
    #                    nomal_trans_conf="../../test/conf/snmp/snmpv3.json", interval=0.03)

    fuzzer = UDPFuzzer("127.0.0.1", 1111, sample_path="../../test/sample/snmp/",
                       nomal_trans_conf="../../test/conf/snmp/snmpv3.json", interval=0.03)
    fuzzer.fuzz()

    fuzzer.check_vuln([{"recv": "61646d696e",
                        "send": "3081b502010330110204009e5d1b020300ffe3040105020103042f302d040d80001f888059dc486145a2632202010802020ab90405706970706f040c055b0aa218fd325bac0dead60400306c040580000000060400a15902042c180dbd020100020100304b300d01040161458363220400a15902042c180dbd020100020100304b300d06092b060102010202352e3235352e30302106122b06352e3235352e30010401817d08330a0201070a86deb738040b3137322e33312e31392e32"}]
                      )
    import sys
    sys.exit()

    maybe_crash_seqs = [[{"recv": "61646d696e",
                          "send": "3081b502010330110204009e5d1b020300ffe3040105020103042f302d040d80001f888059dc486145a2632202010802020ab90405706970706f040c055b0aa218fd325bac0dead60400306c040580000000060400a15902042c180dbd020100020100304b300d01040161458363220400a15902042c180dbd020100020100304b300d06092b060102010202352e3235352e30302106122b06352e3235352e30010401817d08330a0201070a86deb738040b3137322e33312e31392e32"}],
                        [{"recv": "61646d696e",
                          "send": "3040020103300f02030091c8020205dc04010402010304153013040002010002010004fefefefe492cf3b29efbe8d8576bfa7510f25bfe2e1f84fefefefefefefefdfe55885b012337aaff9a52a823201705d0772cdf5273106a6282c73c03006ec80201000201002000"}],
                        [{"recv": "61646d696e",
                          "send": "304002010302000000ff20c2846ddf4b30130400020100020100040561646d696e04000400301304000400a00d0203006ec80201000201002000"}]]

    for seq in maybe_crash_seqs:
        if fuzzer.check_vuln(seq):
            print json.dumps(seq)
            exit()
