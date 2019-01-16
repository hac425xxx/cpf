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

    def __init__(self, host, port, nomal_trans_conf, sample_path="", logseq_count=3, interval=0.01, workspace=""):
        """

        :param host: 目标的 ip
        :param port: 目标的端口
        :param nomal_trans_conf: 交互序列配置文件，可以是目录，或者文件全路径， 如果是目录就加载目录下的所有交互
        :param sample_path: 历史漏洞样本目录路径
        :param logseq_count: 记录最近多少次的样本
        :param interval: 发包间隔
        """

        # 工作目录用于存放运行日志，crash, 后续可能用于记录 log....
        # 目录不存在就创建一个
        self.workspace = workspace
        if self.workspace != "":
            if not os.path.exists(self.workspace):
                os.mkdir(self.workspace)

        # 从交互配置文件里面导入状态信息

        # state_data 是一个数组，每一项代码每个状态下可选数据集合
        self.state_data = []
        # 一个数组，每一项都是一个完整的交互序列
        self.trans = []

        #  如果是目录的话，就加载目录下的所有交互文件，然后合并每个状态下的交互过程， 用来后续 fuzz 时做种子
        if nomal_trans_conf != "":
            if os.path.isdir(nomal_trans_conf):
                trans_contents = []
                for fname in os.listdir(nomal_trans_conf):
                    with open(os.path.join(nomal_trans_conf, fname), "r") as fp:
                        content = json.loads(fp.read())
                        self.welcome_msg = content["welcome_msg"].decode("hex")
                        tran = {
                            "file": fname,
                            "trans": content['trans']
                        }
                        # 保存每个完整的交互序列，用于后续 fuzz
                        self.trans.append(tran)
                        trans_contents.append(content)

                # 下面是合并个状态的交互过程，用来给 fuzz 做种子
                for t in trans_contents:
                    for i, s in enumerate(t['trans']):
                        if len(self.state_data) > i:
                            if s not in self.state_data[i]:
                                self.state_data[i].append(s)
                        else:
                            self.state_data.append([s])

            else:

                # 当提供的是一个文件的情况
                with open(nomal_trans_conf, "r") as fp:
                    content = json.loads(fp.read())
                    self.welcome_msg = content["welcome_msg"].decode("hex")
                    tran = {
                        "file": os.path.basename(nomal_trans_conf),
                        "trans": content['trans']
                    }

                    self.trans.append(tran)
                    self.state_data = []

                    for i, s in enumerate(content["trans"]):
                        if len(self.state_data) > i:
                            if s not in self.state_data[i]:
                                self.state_data[i].append(s)
                        else:
                            self.state_data.append([s])

        # print json.dumps(self.state_data)

        self.samples = []
        self.token = []

        # 加载以后漏洞库的样本路径， 用于 fuzz 时的 种子
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

        # 初始化测试序列日志队列，保存最近3次的测试序列, 设置log目录为 workspace/logs
        self.logger = SequenceLogger(maxlen=logseq_count, log_dir=os.path.join(self.workspace, "logs"))

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

            # 首先随机取一个完整的交互序列
            tran = random.choice(self.trans)['trans']

            # 对这个交互序列下的所有状态进行遍历 fuzz
            for i in xrange(start_state, len(tran)):

                if self.fuzz_count % 10000:
                    self.mutater.mutate_max_count += 1

                print("当前fuzz状态: {}, 此时已经fuzz {} 次".format(i + 1, self.fuzz_count))

                data = {
                    "fuzz_count": self.fuzz_count,
                    "is_run": True,
                }
                with open(os.path.join(self.workspace, "runtime.json"), "w") as fp:
                    fp.write(json.dumps(data))

                # 到达生成当前状态 i 的前序数据包
                pre_seqs = generate_preseqs(tran, i)
                fuzz_seq = {}

                # 计算每个状态 fuzz 的次数
                if max_fuzz_count:
                    test_count = max_fuzz_count / len(tran)
                else:
                    test_count = int(self.perseq_testcount * (i + 1) * 0.8)

                for c in xrange(test_count):
                    # 生成变异后的数据包

                    raw = random.choice(self.state_data[i])['send'].decode("hex")
                    fuzz_seq['recv'] = tran[i]['recv']

                    sample = {}
                    # 根据随机， 看是否用漏洞库里的样本做种子
                    if self.samples and random.randint(0, 20) < 3:
                        sample = random.choice(self.samples)
                        path = sample['path']
                        sample['hit'] += 1
                        with open(path, 'rb') as fp:
                            raw = fp.read()

                    #  如果种子文件是样本，且是第一次使用，就直接重放
                    if sample and i not in sample['state']:
                        fuzz_seq['send'] = raw.encode('hex')
                        sample['state'].append(i)
                    else:
                        # 否则直接变异
                        fuzz_seq['send'] = self.mutater.mutate(raw).encode("hex")

                    # 由于 python 指针传值的原因，需要重新生成对象，避免出现问题
                    # 生成完整的一个 测试序列
                    test_seqs = []
                    test_seqs += pre_seqs
                    test_seqs.append(fuzz_seq)

                    # 发送测试序列
                    if not self.send_to_target(test_seqs):
                        # 如果发送序列失败判断下 服务器是否存活
                        # sleep(0.5)
                        # 如果已经挂了，就重放最近的流量确认不是由于并发导致的原因

                        print("序列发送失败，下面 sleep 一下，让服务器休息会")
                        # 休息一段时间，然后重放测试用例
                        sleep(1.0 * self.exception_count)
                        self.exception_count += 1

                        if self.exception_count > 6:
                            print("*" * 20)
                            print("发送数据失败次数已达上限，服务貌似已经挂了， 退出")
                            print("*" * 20)
                            seqs = self.logger.dump_sequence()
                            print("测试: {} 次, 异常序列: {}".format(self.fuzz_count, json.dumps(seqs)))

                            self.save_crash(seqs, "timeout")

                            self.logger.exit_thread()
                            raise Exception("服务貌似已经挂了， 退出")

                            # if self.check_again(seqs):
                            #     print("测试: {} 次, 异常序列: {}".format(self.fuzz_count, json.dumps(seqs)))
                            #     raise Exception("服务貌似已经挂了， 退出")

                    else:
                        self.logger.add_to_queue(test_seqs)
                        if not self.is_alive():
                            # 如果不存活了就认为触发了异常， 保存最近的测试序列
                            seqs = self.logger.dump_sequence()
                            # 休息一段时间，然后重放测试用例
                            sleep(1.0 * self.exception_count)
                            if self.check_again(seqs):
                                print("测试: {} 次, 异常序列: {}".format(self.fuzz_count, json.dumps(seqs)))

                                self.save_crash(seqs, "crash")

                                self.logger.exit_thread()
                                raise Exception("服务貌似已经挂了， 退出")
                        if self.exception_count > 2:
                            self.exception_count -= 2

    def save_crash(self, seqs, type):
        normal_configure = {
            "trans": self.trans[0]['trans'],
            "welcome_msg": self.welcome_msg.encode("hex")
        }
        data = {
            "type": type,
            "fuzz_count": self.fuzz_count,
            "is_run": False,
            "normal_configure": normal_configure,
            "crash_sequence": seqs
        }
        with open(os.path.join(self.workspace, "runtime.json"), "w") as fp:
            fp.write(json.dumps(data))

    def send_to_target(self, test_seqs):
        """
        发送数据包序列
        :param test_seqs:
        :return: 如果发送成功返回 True, 失败返回 False
        """

        #  发送数据包序列前，把当前要发送序列存入 最大长度为 3 的队列里面， 用于后续记录日志

        try:
            p = TCPCommunicator(self.host, self.port, interval=self.interval)

            # 如果服务器有欢迎消息，即欢迎消息非空，就先接收欢迎消息
            if self.welcome_msg:
                # 获取欢迎消息
                data = p.recv(1024)
                while self.welcome_msg not in data:
                    data = p.recv(1024)
            else:
                sleep(0.2)

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
            self.fuzz_count += 1

            return True
        except Exception as e:
            print e
            self.exception_count += 1
            return False

    def is_alive(self):
        """
        判断目标是否存活
        :return: 如果存活返回 True, 否则返回 False
        """

        # 首先检查端口是否开放
        if check_tcp_port(self.host, self.port):
            data = ""
            count = 0

            while count < 3:
                try:
                    p = TCPCommunicator(self.host, self.port)
                    # 如果服务器有欢迎消息，即欢迎消息非空，就先接收欢迎消息
                    if self.welcome_msg:
                        # 获取欢迎消息
                        data = p.recv(1024)
                        if self.welcome_msg not in data:
                            raise Exception("欢迎消息接收失败")
                    else:
                        tran = self.trans[0]['trans']
                        for s in tran:
                            p.send(s['send'].decode('hex'))
                            data = p.recv(1024)
                            if s['recv'] not in data.encode('hex'):
                                raise Exception("except: {}, actal recv: {}".format(s['recv'], data.encode('hex')))
                    del p
                    return True
                except Exception as e:
                    count += 1
                    sleep(0.6)
                    continue
        self.exception_count += 1
        return False

    def check_again(self, trans):
        """

        :param trans:
        :return: 如果返回 True 说明目标已经挂，
        """

        if not self.is_alive():
            return True

        #  首先遍历 trans , 因为传入的 trans 是有 logger dump出来的最近几次的发包序列
        # 这里对每次的发包序列进行重放
        for seqs in trans:
            # 如果测试目标已经挂了，就不用重放了

            try:
                sleep(1.0 * self.exception_count)
                self.send_to_target(seqs)
                # 检测是否存活
                if not self.is_alive():
                    return True
            except Exception as e:
                print e
                return True

        return False

    def check_vuln(self, seqs, wait_time=1):
        """
        通过重放序列来重现漏洞
        :param seqs: 一个完成的交互数据包序列
        :return: 如果漏洞存在返回 True
        """
        if self.send_to_target(seqs):
            print("发包成功，下面测试服务是否存活")
            sleep(wait_time)
            if self.is_alive():
                return False
            print("噢， 服务挂了")
        return True


if __name__ == '__main__':
    fuzzer = TCPFuzzer("192.168.245.131", 21, nomal_trans_conf="/fuzzer/test/conf/floatftp", interval=0)

    # fuzzer.fuzz()

    print fuzzer.check_vuln([{"recv": "50617373776f7264207265717569726564", "send": "5553455220667265650D0A"},
                             {"recv": "6c6f6767656420696e", "send": "5041535320667265650D0A"}, {"recv": "",
                                                                                                "send": "4c41414141cd401715de0160606060f1797458392e3a2b302dde9bf22b6771caadf80631780fd0b6a8557e1d3539ffffffffffffffffb6904edb30dec2b27386f15291ab4b73201f55073bc5c937a1eda42bf1fb0737702df15291ab4b73201f55073bc511eab2391d28f6e86d9ea79f9ac4179cdf2e4b51958c1acf58effefefefefefefefefefefefefefefefefefefefefefefefefefefefefea42bf1fb0737702df15291ab4b73201f55073bc511eab2391d28f6e86d9ea79f9ac4179cdf2e4b51958c1acf58effefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefe14a5459d41411bdeb85c25e9e55a0d"}])
    exit(0)

    maybe_crash_seqs = [[{"recv": "50617373776f7264207265717569726564",
                          "send": "15ac53f8e3b610d2fefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefeaa7772fefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefefe3f3f3ff40de3b610d24125e45553f8e4b655acf852ff0000"}],
                        [{"recv": "50617373776f7264207265717569726564", "send": "ce"}], [
                            {"recv": "50617373776f7264207265717569726564",
                             "send": "ffffffffff3bffffffffffff77b6e9fffffe00ff12ffffffff202020202020202020202020a4202020ffffffffffffff6bffffffffffffff3bffffffffffff77b6e9fffffe00ff12ffffffff2020202020202020"}],
                        [{"recv": "50617373776f7264207265717569726564",
                          "send": "d53fd5a993c4b212024823f411540b585f6060605c6f0b585f60ffffd99185ab"}], [
                            {"recv": "50617373776f7264207265717569726564",
                             "send": "2020000000000000007e202000010000000000"}]]
    for seq in maybe_crash_seqs:
        if fuzzer.check_vuln(seq):
            print json.dumps(seq)
            exit(0)
