#!/usr/bin/python
# -*- coding: UTF-8 -*-

from cpf.fuzzer.TCPFuzzer import TCPFuzzer

if __name__ == '__main__':

    fuzzer = TCPFuzzer(host="192.168.245.135", port=27700,
                       nomal_trans_conf="conf/seigmodbus.json",
                       logseq_count=3)

    relay = False

    if not relay:
        fuzzer.fuzz(mutate_max_count=10)
    else:

        seqs = [[{"recv": "66726565", "send": "5553455220667265650D0A"},
                 {"recv": "6f67676564", "send": "5041535320667265650D0A"},
                 {"recv": "",
                  "send": "00AA00BB00CC00DD00DD0ADFA0D0F0ADF0A0DF0ADFA8D0F80808134813417350183417329471938510"}]]

    for seq in seqs:
        fuzzer.replay(seq)
