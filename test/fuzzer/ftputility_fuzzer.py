#!/usr/bin/python
# -*- coding: UTF-8 -*-

from cpf.fuzzer.TCPFuzzer import TCPFuzzer
import json

COMMAND = ""


def fuzz_command(data):
    # 将变异后的数据增加到被测命令的后面
    return "{} ".format(COMMAND) + data


if __name__ == '__main__':

    fuzzer = TCPFuzzer(host="192.168.245.135", port=21,
                       nomal_trans_conf="conf/ftputility.json",
                       logseq_count=3)

    relay = True

    if not relay:

        COMMAND = "CWD"
        print("开始fuzz: {}".format(COMMAND))
        fuzzer.fuzz(start_state=2, mutate_max_count=10, callback=fuzz_command)
        fuzzer.fuzz_count = 0
    else:

        trans = [[{"recv": "66726565", "send": "5553455220667265650D0A"},
                  {"recv": "6f67676564", "send": "5041535320667265650D0A"},
                  {"recv": "", "send": "4357442009c4f4f4d6b754"}],
                 [{"recv": "66726565", "send": "5553455220667265650D0A"},
                  {"recv": "6f67676564", "send": "5041535320667265650D0A"}, {"recv": "",
                                                                             "send": "4357442020611c6369c99422cb6b9c3321b9bd391666b07ffb298629f7cad72ab8ec2afea68891e0165c6ce313c4f03ab2fd882857827ef03b78da294f19f7f24a1defafe353e163dbbcb9aae4e48587f6ca16c87302798e6a54ffaea6ad13acd8e937a6f4433b392557d0770ebfa29270dc173958a34b103264665236de95482b7ee5885b4ca69bb6e87ffa6afe70986ebc8bff6ebb426c30766c93f7b5046b3905fd1b3f2f416075afeaf620fa9a84cddf27510177c8ffeef2f0c10cb2b59b31011d0dc5972717b9f6db75aad68c6e303ccbdf5483edca9a0193da24372a93439dbf2f84d38cacb98b0eba47076725a9f79579d542b36b68a4a1754b55ff7439022d643b397d9c7e5e1ad6200fefae1efbf00d745c3188b15a2ef1602b32f94f0927cac530d257f81a208e651a300ff26b36630f4cf152d481757f11f581d4f6fdfdb51dcde776dcb33a2d2259198bf24f79d55ca047b014ffffffffffffffffb853321f37ac7b970237c9ab2282024e4dd562ff9997da2fc3888302c824d7da35fdb4214fd9f0f76e04f53ab23ef6c6b23eeb9e9782d36d3f7d3ded2eadb120b07ffb298629f7cad71c6369c99422cb6b9c3321b9bd391666b07ffb298629f7cad72ab8ec2afea68891e0165c6ce313c4f03ab2fd882857827ef03b78da294f19f7f24a1defafe353e163dbbcb9aae4e48587f6ca16c87302798e6a54ffaea6ad13acd8e937a6f4433b392557d0770ebfa29270dc173958a34b103264665236de95482b7ee5885b4ca69bb6e87ffa6afe70986ebc8bff6ebb426c30766c93f7b5046b3905fd1b3f2f416075afeaf620fa9a84cddf27510177c8ffeef2f0c10cb2b59b31011d0dc5972717b9f6db75aad68c6e303ccbdf5483edca9a0193da24372a93439dbf2f84d38cacb98b0eba47076725a9f79579d542b36b68a4a1754b55ff7439022d643b397d9c7e5e1ad6200fefae1efbf00d745c3188b15a2ef1602b32f94f09274ac530d257f81a208e651a300ff26b36630f4cf152d481757f11f581d4f6fdfdb51dcde776dcb33a2d2259198bf24f79d55ca047b014ffffffffffffffffb853321f37ac7b970237c9ab2282024e4dd562ff9997da2fc3888302c824d7da35fdb4214fd9f0f76e04f53ab23ef6c6b23eeb9e9782d36d3f7d3ded2eadb120b07ffb298629f7cad72ab8ec2afea68891e0165c6ce313c4f03ab2fd882857827ef03b78da29651a300ff26b36630f4cf152d481757f11f581d4f6fdfdb51dcde776dcb33a2d2259198bf24f79d55ca047b014ffffffffffffffffb853321f37ac7b970237c9ab2282024e4dd562ff9997da2fc3888302c824d7da35fd2ab8ec2afea68891e0165c6ce313c4f03ab2fd882857827ef03b78da29651a300ff26b36630f4cf152d481757f11f581d4f6fdfdb51ddde776dcb33a2d2259198bf24f79d55ca047b014ffffffffffffffffb853321f37ac7b970237c9ab2282024e4dd562ff9997da2fc3888302c824d7da35fdb4214fd9f0f76e04f53a"}],
                 [{"recv": "66726565", "send": "5553455220667265650D0A"},
                  {"recv": "6f67676564", "send": "5041535320667265650D0A"},
                  {"recv": "", "send": "4357442020202020d94374feec68b1d9a17b97f85784ece0c1f8559b830bc7ff6a05"}]]
    for seqs in trans:
        if fuzzer.check_vuln(seqs):
            print seqs
            exit(0)
