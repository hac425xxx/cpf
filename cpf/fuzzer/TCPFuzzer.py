#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from cpf.mutate.Mutater import Mutater
from cpf.misc.utils import generate_preseqs
from cpf.misc.SequenceLogger import SequenceLogger
from cpf.protocol.network.TCPCommunicator import TCPCommunicator


class TCPFuzzer:

    def __init__(self, host, port, trans_file_path, mutate_max_count=25, perseq_testcount=200):
        # 从交互配置文件里面导入信息
        with open(trans_file_path, "r") as fp:
            trans_data = json.loads(fp.read())
            self.end_stats = trans_data["end_states"]
            self.welcome_msg = trans_data["welcome_msg"].decode("hex")
            self.trans = trans_data["trans"]

        # 初始化测试序列日志队列，保存最近3次的测试序列
        self.logger = SequenceLogger(maxlen=3)
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

                if self.mutater.mutate_max_count >= self.mutate_max_count:
                    self.mutater.mutate_max_count = 6

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

                        # 发送测试序列
                        self.send_seqs(test_seqs)

                        # 检测是否存活
                        if not self.is_alive():
                            self.logger.dump_sequence()
                            exit(0)

                    except Exception as e:
                        print e

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
        except:
            return False

    def replay(self, seqs):

        self.send_seqs(seqs)

        # 检测是否存活
        if not self.is_alive():
            self.logger.dump_sequence()
            exit(0)


if __name__ == '__main__':
    fuzzer = TCPFuzzer(host="192.168.245.131", port=21, trans_file_path="../../test/data/Slyar_ftp.json")
    fuzzer.fuzz()
    # fuzzer.replay(seqs)
