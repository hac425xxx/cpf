#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from time import sleep
from cpf.mutate.Mutater import Mutater
from cpf.misc.utils import *
from cpf.misc.SequenceLogger import SequenceLogger
from cpf.protocol.network.TCPCommunicator import TCPCommunicator
import random, os


class TCPFuzzer:

    def __init__(self, host, port, nomal_trans_conf, sample_path="", logseq_count=3, interval=0.01):
        """

        :param host: 目标的 ip
        :param port: 目标的端口
        :param nomal_trans_conf: 一个正常交互过程的序列配置文件
        :param logseq_count: 记录最近多少次的样本
        :param mutate_max_count: 变异的最大次数
        :param perseq_testcount: 一次循环对每个状态的变异测试
        """
        # 从交互配置文件里面导入状态信息
        with open(nomal_trans_conf, "r") as fp:
            trans_data = json.loads(fp.read())
            self.end_stats = trans_data["end_states"]
            self.welcome_msg = trans_data["welcome_msg"].decode("hex")
            self.trans = trans_data["trans"]

        self.samples = []
        self.token = []
        if sample_path:

            if os.path.exists(os.path.join(sample_path, "token.json")):
                # 首先从 token.json 加载相应的 token
                with open(os.path.join(sample_path, "token.json")) as fp:
                    for i in json.loads(fp.read()):
                        if i['type'] == "plain":
                            self.token.append(i["value"])
                        else:
                            self.token.append(i["value"].decode("hex"))

            for p in os.listdir(sample_path):
                if "token.json" in p:
                    continue

                sample = {}
                sample['state'] = []
                sample['path'] = os.path.join(sample_path, p)
                sample['hit'] = 0

                # 把路径加到 samples 里面，供后续取用
                self.samples.append(sample)

        # 初始化测试序列日志队列，保存最近3次的测试序列
        self.logger = SequenceLogger(maxlen=logseq_count)

        self.host = host
        self.port = port

        self.interval = interval

        # 计数器，记录 fuzz 次数
        self.fuzz_count = 0
        self.exception_count = 1

    def fuzz(self, start_state=0, callback=None, mutate_max_count=25, perseq_testcount=200,
             max_fuzz_count=None):
        """

        :param interval: 每次发包的间隔时间， sleep(.)
        :param start_state:
        :param callback: 函数指针，用于对数据进行修正， 接收一个参数（变异后的数据）， 返回 修正过的数据
        :param mutate_max_count:
        :param perseq_testcount:
        :return:
        """

        self.perseq_testcount = perseq_testcount
        self.mutater = Mutater(mutate_max_count=mutate_max_count, callback=callback)

        while True:

            if max_fuzz_count and max_fuzz_count <= self.fuzz_count:
                return True

            # 遍历整个 trans
            for i in xrange(start_state, len(self.trans)):

                if self.fuzz_count % 10000:
                    self.mutater.mutate_max_count += 1

                print("当前fuzz状态: {}, 此时已经fuzz {} 次".format(self.trans[i]['state'], self.fuzz_count))

                init_case = self.trans[i]['send'].decode("hex")

                # 到达生成当前状态的前序数据包
                pre_seqs = generate_preseqs(self.trans, i)

                fuzz_seq = {}

                # 计算每个状态 fuzz 的次数
                if max_fuzz_count:
                    test_count = max_fuzz_count / len(self.trans)
                else:
                    test_count = int(self.perseq_testcount * (i + 1) * 0.8)

                for c in xrange(test_count):
                    # 生成变异后的数据包
                    raw = init_case
                    sample = {}
                    if self.samples and random.randint(0, 1):
                        sample = random.choice(self.samples)
                        path = sample['path']
                        sample['hit'] += 1
                        with open(path, 'rb') as fp:
                            raw = fp.read()

                    if sample and i not in sample['state']:
                        fuzz_seq['send'] = raw.encode('hex')
                        sample['state'].append(i)
                    else:
                        fuzz_seq['send'] = self.mutater.mutate(raw).encode("hex")

                    fuzz_seq['recv'] = self.trans[i]['recv']

                    # 由于 python 指针传值的原因，需要重新生成对象，避免出现问题
                    test_seqs = []
                    test_seqs += pre_seqs
                    test_seqs.append(fuzz_seq)

                    if self.exception_count > 6:
                        print("*" * 20)
                        print("发送数据失败次数已达上限，服务貌似已经挂了， 退出")
                        print("*" * 20)
                        exit(0)

                    # 发送测试序列
                    if not self.send_seqs(test_seqs):

                        sleep(0.5)
                        # 如果已经挂了，就重放最近的流量确认不是由于并发导致的原因
                        if not self.is_alive():
                            seqs = self.logger.dump_sequence()
                            sleep(1.0 * self.exception_count)
                            if self.check_again(seqs):
                                print("测试: {} 次, 异常序列: {}".format(self.fuzz_count, json.dumps(seqs)))

                    else:

                        if self.exception_count > 2:
                            self.exception_count -= 2

    def send_seqs(self, test_seqs):
        """
        发送数据包序列
        :param test_seqs:
        :return: 如果发送成功返回 True, 失败返回 False
        """
        self.fuzz_count += 1

        #  发送数据包序列前，把当前要发送序列存入 最大长度为 3 的队列里面， 用于后续记录日志

        try:
            p = TCPCommunicator(self.host, self.port, interval=self.interval)

            self.logger.add_to_queue(test_seqs)
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
                    print("*" * 20)
                    print("与服务器前序交互异常，下面是日志")
                    print("应该接受的回应：{}\n实际接收的回应：{}".format(seq['recv'], data.encode("hex")))
                    print("*" * 20)
            # 发送 fuzz 数据包， 即最后一个数据包
            p.send(test_seqs[-1]['send'].decode('hex'))

            del p
            return True
        except Exception as e:
            self.exception_count += 1
            return False

    def is_alive(self):
        if check_tcp_port(self.host, self.port):
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
                # raise e
                self.exception_count += 1
                return False
        else:
            return False

    def check_again(self, trans):
        """

        :param trans:
        :return: 如果返回 True 说明目标已经挂，
        """
        #  首先遍历 trans , 因为传入的 trans 是有 logger dump出来的最近几次的发包序列
        # 这里对每次的发包序列进行重放
        for seqs in trans:
            # 如果测试目标已经挂了，就不用重放了
            if self.is_alive():
                try:
                    sleep(1.0 * self.exception_count)
                    self.send_seqs(seqs)
                    # 检测是否存活
                    if not self.is_alive():
                        return True
                except Exception as e:
                    print e
                    return True
            else:
                return True

        return False

    def check_vuln(self, seqs):
        """
        通过重放序列来重现漏洞
        :param seqs: 一个完成的交互数据包序列
        :return: 如果漏洞存在返回 True
        """
        if self.send_seqs(seqs):
            # print("发包成功，下面测试服务是否存活")

            if self.is_alive():
                return False
            print("噢， 服务挂了")
        return True


if __name__ == '__main__':
    # fuzzer = TCPFuzzer(host="192.168.245.131", port=21,
    #                    sample_path="../../test/sample/ftp",
    #                    nomal_trans_conf="../../test/conf/coreftp.json",
    #                    logseq_count=5)

    fuzzer = TCPFuzzer(host="192.168.245.135", port=21,
                       sample_path="../../test/sample/ftp",
                       nomal_trans_conf="../../test/conf/ftputility.json",
                       logseq_count=5)

    # fuzzer = TCPFuzzer(host="192.168.245.141", port=777, trans_file_path="../../test/conf/kingview.json",
    #                    mutate_max_count=40)

    # fuzzer = TCPFuzzer(host="192.168.245.131", port=8888, nomal_trans_conf="../../test/conf/http.json", logseq_count=3)

    relay = False

    if not relay:
        fuzzer.fuzz(start_state=2, mutate_max_count=10)
    else:

        seqs = [[{"recv": "70617373776f7264",
                  "send": "4c49535420414141414141417730307477303074e431cef321327aaa919ab5d42a5a747914785a93d78f782e3e3063f75cd78f782e3e3063f75c597f87dfff8f22f48668d378332420202020202020202020202020202020fe202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020203420202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202041414141414141202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202034202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020"}]]

        for seq in seqs:
            fuzzer.check_vuln(seq)
