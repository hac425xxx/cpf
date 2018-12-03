#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from time import sleep
from cpf.mutate.Mutater import Mutater
from cpf.misc.utils import generate_preseqs
from cpf.misc.SequenceLogger import SequenceLogger
from cpf.protocol.network.TCPCommunicator import TCPCommunicator


class TCPFuzzer:

    def __init__(self, host, port, trans_file_path, logseq_count=3, mutate_max_count=25, perseq_testcount=200):
        # 从交互配置文件里面导入信息
        with open(trans_file_path, "r") as fp:
            trans_data = json.loads(fp.read())
            self.end_stats = trans_data["end_states"]
            self.welcome_msg = trans_data["welcome_msg"].decode("hex")
            self.trans = trans_data["trans"]

        # 初始化测试序列日志队列，保存最近3次的测试序列
        self.logger = SequenceLogger(maxlen=logseq_count)
        self.mutater = Mutater()

        self.host = host
        self.port = port

        # 计数器，记录 fuzz 次数
        self.fuzz_count = 0

        self.perseq_testcount = perseq_testcount
        self.mutate_max_count = mutate_max_count

    def fuzz(self):
        while True:

            # 遍历整个 trans
            for i in xrange(len(self.trans)):

                if self.fuzz_count % 10000:
                    self.mutater.mutate_max_count += 1

                print("当前fuzz状态: {}, 此时已经fuzz {} 次".format(self.trans[i]['state'], self.fuzz_count))

                init_case = self.trans[i]['send'].decode("hex")

                # 到达生成当前状态的前序数据包
                pre_seqs = generate_preseqs(self.trans, i)

                fuzz_seq = {}

                # 更加 test_count 觉定在当前状态的 fuzz 次数
                for c in xrange(self.perseq_testcount):
                    # 生成变异后的数据包

                    fuzz_seq['send'] = self.mutater.mutate(init_case).encode("hex")
                    fuzz_seq['recv'] = self.trans[i]['recv']

                    # 由于 python 指针传值的原因，需要重新生成对象，避免出现问题
                    test_seqs = []
                    test_seqs += pre_seqs
                    test_seqs.append(fuzz_seq)

                    try:
                        # sleep(0.2)
                        # 发送测试序列
                        self.send_seqs(test_seqs)

                        # sleep(0.1)
                        # 检测是否存活
                        if not self.is_alive():
                            self.logger.dump_sequence()
                            exit(0)

                    except Exception as e:
                        self.logger.dump_sequence()
                        print "发送数据包时异常, {}".format(e)
                        exit(0)

    def send_seqs(self, test_seqs):

        self.fuzz_count += 1

        #  发送数据包序列前，把当前要发送序列存入 最大长度为 3 的队列里面， 用于后续记录日志
        self.logger.add_to_queue(test_seqs)

        p = TCPCommunicator(self.host, self.port)

        # 如果服务器有欢迎消息，即欢迎消息非空，就先接收欢迎消息
        if self.welcome_msg:
            # 获取欢迎消息
            data = p.recv(1024)
            while self.welcome_msg not in data:
                data = p.recv(1024)

        # 发送前序数据包序列
        for seq in test_seqs[:-1]:
            p.send(seq['send'].decode('hex'))
            data = p.recv(1024)
            if seq['recv'].decode('hex') not in data:
                print("@{}@----@{}@".format(seq['recv'], data.encode("hex")))
        # 发送 fuzz 数据包， 即最后一个数据包
        p.send(test_seqs[-1]['send'].decode('hex'))

        del p

    def is_alive(self):

        try:
            p = TCPCommunicator(self.host, self.port)
            # 如果服务器有欢迎消息，即欢迎消息非空，就先接收欢迎消息
            if self.welcome_msg:
                # 获取欢迎消息
                data = p.recv(1024)
                while self.welcome_msg not in data:
                    data = p.recv(1024)
            del p
            return True
        except Exception as e:
            print e
            return False

    def replay(self, seqs):

        self.send_seqs(seqs)

        # 检测是否存活
        if not self.is_alive():
            self.logger.dump_sequence()
            exit(0)


if __name__ == '__main__':
    # fuzzer = TCPFuzzer(host="192.168.245.131", port=21, trans_file_path="../../test/data/float_ftp.json",
    #                    logseq_count=5, mutate_max_count=9)

    # fuzzer = TCPFuzzer(host="192.168.245.141", port=777, trans_file_path="../../test/data/kingview.json",
    #                    mutate_max_count=40)

    fuzzer = TCPFuzzer(host="192.168.245.131", port=8888, trans_file_path="../../test/data/http.json", logseq_count=3)

    relay = True

    if not relay:
        fuzzer.fuzz()
    else:

        seqs = [[{"recv": "68746d6c", "send": "47456e678f7a2f3d6363652a3b713d6363656f677a"}],
                [{"recv": "68746d6c", "send": "474554202f380d0aa80a54242e38"}], [{"recv": "68746d6c",
                                                                                  "send": "474554202f20485454502f312e310d0a486f73743a203139322e3136382e3234352e3133310d0a436f6e6e656374696f6e3a209a1be4cd8a7d49517b0c60606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060736460606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060606060604efedb83c8ab07cac89a1b1b0ffd419aae21e409fdee1116822209754c12dc27c524871dc592e726cf1eaa0dfc18ac471be912e6063a53f44bb23876f260d7fe1ec44a77702419b8e4c8feb368660c0f00a4de03abb3a1625e7a512967d935f27e4d987823523adb4b22126aa80821b655f7dbdd86f5b101f1e063f093ba916644673211dcfe5b05eda9b92806cbb6351521873906fa4d728be49d057614b185e94f5f54321cde0b6719bafdebd556695d0dda18b77aebfd3775eb2f9182591bfa2cf4b3226c105735ae53816c4ae8b5859ce0694ebb348b88da54ed7428c5feb5da3a1e344fb633871f8803a4a7545caeb8b938518c4c92b6d95c281ae86c91f171b61e5035d7dc7f484f7462318c01c4c34ae3187eae6a9da7bae5bdb625c0aae4f899f9511d980f062a9fc3c3a28edf78f9dbc501b724358cde26a8d868401e5beec1c0a26f764fb7f739016ca6eb4579d8c9d1587bf659a873bcada8afdac1d99b47de68e22e6e672e84884912ba9e61921c0110ca483756f2b79e4cf7db1d4eb6d72b43ccdea4aa7167cf7ad01ef26fa2bbc54a094e3dd205cf9fc589f95db8b15ba148a276bf3364fca6b2205fb82d066ef5d9c6be96165f78a63a58ff0c5b6df9692ae0e7270300fe6cf028b3cc33ab372010abb85b65e3003c3a5244cab553e687d1c7b60c6060606060606060606060606060606060606060606060606060606060606060606060607a683b713d302e392c656e3b713d302e380d0a0d0a"}]]

        for seq in seqs:
            fuzzer.replay(seq)
