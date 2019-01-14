#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import time
import random
import json
import usb.core
import binascii
from scapy.packet import Raw, fuzz
from cpf.mutate.Mutater import Mutater
from cpf.misc.SequenceLogger import SequenceLogger
from cpf.protocol.usb.CCID import *
from cpf.protocol.usb.QCDM import *
from cpf.protocol.usb.MTP import *
from cpf.protocol.usb.MSC import *
from cpf.misc.utils import *
from time import sleep


class CtrlFuzzer:
    def __init__(self, idVendor, idProduct, workspace=""):
        """

        :param idVendor: 设备的 idVendor ， int
        :param idProduct: 设备的 idProduct ， int
        :param initq:
        :param initv:
        :param initvv:
        """
        self.device = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        self.mutater = Mutater()
        self.fuzz_count = 0

        self.workspace = workspace
        # 工作目录用于存放运行日志，crash, 后续可能用于记录 log....
        # 目录不存在就创建一个
        self.workspace = workspace
        if self.workspace != "":
            if not os.path.exists(self.workspace):
                os.mkdir(self.workspace)
        self.logger = SequenceLogger(log_dir=os.path.join(self.workspace, "logs"))

    def fuzz(self):

        while True:

            if self.fuzz_count % 200 == 0:
                print "已经测试: {} 次".format(self.fuzz_count)
                data = {
                    "fuzz_count": self.fuzz_count,
                    "is_run": True,
                }
                with open(os.path.join(self.workspace, "runtime.json"), "w") as fp:
                    fp.write(json.dumps(data))

            data = self.mutater.mutate("80060100000034343434343434".decode("hex"))
            if len(data) < 7:
                continue

            bRequest = int(data[1].encode("hex"), 16)
            wValue = int(data[2:4].encode("hex"), 16)
            wIndex = int(data[4:6].encode("hex"), 16)
            bmRequestType = int(data[0].encode("hex"), 16)

            try:
                self.logger.add_to_queue(data.encode("hex"))
                res = self.device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data[6:], timeout=250)
                self.fuzz_count += 1
            except usb.core.USBError as e:
                if e.backend_error_code != -9 and e.backend_error_code != -1:  # ignore LIBUSB_ERROR_PIPE and LIBUSB_ERROR_IO
                    pass
            except AttributeError:
                print "设备获取失败, 请确认设备已经插上"
                exit(0)

            if not self.is_alive():
                seqs = self.logger.dump_sequence()

                data = {
                    "fuzz_count": self.fuzz_count,
                    "is_run": False,
                    "crash_sequence": seqs
                }
                with open(os.path.join(self.workspace, "runtime.json"), "w") as fp:
                    fp.write(json.dumps(data))

                print "设备已经挂了"
                print "crash用例： {}".format(json.dumps(seqs))

                self.save_crash(seqs)

                return True

                # self.device.reset()
                # time.sleep(1)

    def check_vuln(self, data):
        data = data.decode('hex')
        bmRequestType = int(data[0].encode("hex"), 16)
        bRequest = int(data[1].encode("hex"), 16)
        wValue = int(data[2:4].encode("hex"), 16)
        wIndex = int(data[4:6].encode("hex"), 16)

        try:
            self.logger.add_to_queue(data.encode("hex"))
            res = self.device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data[6:], timeout=250)
        except usb.core.USBError as e:
            pass

        if not self.is_alive():
            print "造成异常的用例：{}".format(data.encode('hex'))
            return True
        else:
            return False

    def is_alive(self):
        res = ""

        count = 0

        while count < 3:

            try:
                self.device.reset()
                return True
            except Exception as e:
                print e
                count += 1
                sleep(0.5)

        return False

    def save_crash(self, seqs):

        data = {
            "usb_fuzz_type": "CtrlFuzzer",
            "fuzz_count": self.fuzz_count,
            "is_run": False,
            "crash_sequence": seqs
        }
        with open(os.path.join(self.workspace, "runtime.json"), "w") as fp:
            fp.write(json.dumps(data))


class CCIDFuzzer:
    def __init__(self, vid, pid, timeout=2000):
        """

        :param vid:  设备的 vid , 类型 int
        :param pid: 设备的 pid , 类型 int
        :param timeout:
        """
        self.dev = CCIDDevice(vid=hex(vid), pid=hex(pid), timeout=timeout)
        self.logger = SequenceLogger()
        self.dev.reset()

    def fuzz(self):
        while True:

            cmd = CCID(bSeq=self.dev.next_seq(), bSlot=0) / PC_to_RDR_XfrBlock() / fuzz(APDU(CLA=0x80))
            # 做个记录
            self.logger.add_to_queue(str(cmd).encode("hex"))
            self.dev.send(str(cmd))
            res = self.dev.recv()

            if (len(res)):
                reply = CCID(res)
                if Raw in reply and reply[Raw].load[0] != '\x6D':
                    cmd.show2()
                    print self.dev.hex_dump(str(cmd))
                    reply.show2()
                    if Raw in reply:
                        print self.dev.hex_dump(str(reply[Raw]))
            else:
                print "No response to command %u!" % self.dev.cur_seq()
                cmd.show2()

            if not self.dev.is_alive():
                print "设备未存活，下面打印最近的发包序列"
                print self.logger.dump_sequence()


class QCDMFuzzer:
    def __init__(self, vid, pid, iface=0):
        """

        :param vid:  设备的 vid , 类型 int
        :param pid: 设备的 pid , 类型 int
        :param iface:
        """
        self.dev = QCDMDevice(vid=hex(vid), pid=hex(pid), iface=iface)
        self.logger = SequenceLogger()

    def fuzz(self):
        while True:

            cmd = QCDMFrame() / fuzz(Command()) / Raw(os.urandom(8))

            # avoid switching to downloader or test modes
            if cmd.code == 58 or cmd.code == 59:
                cmd.code = 0

                # 做个记录
                self.logger.add_to_queue(str(cmd).encode("hex"))
            self.dev.send(str(cmd))
            res = self.dev.receive_response()

            if QCDMFrame in res:
                res.show()
                if Raw in res:
                    print self.dev.hex_dump(str(res[Raw]))
            else:
                print "No response to command!"
                print self.dev.hex_dump(str(res))

            if not self.dev.is_alive():
                print "设备未存活，下面打印最近的发包序列"
                print self.logger.dump_sequence()


class MTPFuzzer:
    def __init__(self, vid, pid, wait=50, timeout=50):
        self.logger = SequenceLogger()
        self.dev = MTPDevice(vid=hex(vid), pid=hex(pid), wait=wait, timeout=timeout)
        self.dev.reset()

        # open a session
        s = self.dev.new_session()
        cmd = Container() / Operation(OpCode=OpCodes["OpenSession"], Parameter1=s)
        self.dev.send(cmd)

        response = self.dev.read_response()
        if len(response[0]) != 12 or response[0].Code != ResCodes["OK"]:
            print "Error opening session!"
            for packet in response:
                packet.show()
            sys.exit()

    def fuzz(self):

        while True:
            trans = struct.unpack("I", os.urandom(4))[0]
            r = struct.unpack("H", os.urandom(2))[0]

            # 随机取一个 opcode
            opcode = OpCodes.items()[r % len(OpCodes)][1]

            if opcode == OpCodes["CloseSession"]:
                opcode = 0
            cmd = Container() / fuzz(
                Operation(OpCode=opcode, TransactionID=trans, SessionID=self.dev.current_session()))

            self.logger.add_to_queue(str(cmd).encode("hex"))
            self.dev.send(cmd)
            response = self.dev.read_response(trans)

            if len(response) == 0:
                print "No response to transaction %u" % trans
            elif response[-1].Type == 3 and response[-1].Code == ResCodes["Operation_Not_Supported"]:
                print "Operation %x not supported!" % cmd.OpCode
            else:
                cmd.show2()
                for packet in response:
                    if packet.Type == 2:
                        print self.dev.hex_dump(str(packet.payload))
                    else:
                        packet.show()

            if not self.dev.is_alive():
                print "设备未存活，下面打印最近的发包序列"
                print self.logger.dump_sequence()


class MSCFuzzer:

    def __init__(self, vid, pid, timeout=1200):
        self.dev = BOMSDevice(hex(vid), hex(pid), timeout=timeout)
        self.mutater = Mutater()
        self.logger = SequenceLogger()
        # 初始化 pipe
        self.dev.boms_reset()

        # 利用 ReadCapacity 指令，获取设备的信息
        cmd = MSCCBW() / SCSICmd() / ReadCapacity10()
        # print str(cmd).encode("hex")
        self.dev.send(cmd)
        reply = self.dev.read_reply()
        if self.dev.check_status(reply):
            print "设备初始化异常"

        if Raw in reply and len(reply[Raw]) == 8:
            # 获取到 一些设备的信息，
            data = str(reply[Raw])
            max_lba = struct.unpack(">I", data[:4])[0]
            block_size = struct.unpack(">I", data[4:])[0]
            print "Device is %uMb, max LBA is %x and blocksize is %x" % (
                round(float(max_lba * block_size) / 1048576), max_lba, block_size)
        else:
            print "初始化失败"
            reply.show()
            exit(0)

    def fuzz(self):

        count = 0
        while True:
            try:
                count += 1
                print "测试次数：{}".format(count)

                cmd = self.mutater.mutate(
                    "5553424301000000f2f58fd780000b95ae3ebdf5af023a8b844d0000000000".decode("hex"))

                print str(cmd).encode("hex")

                # 发送变异数据
                self.dev.send(cmd)
                self.logger.add_to_queue(str(cmd).encode("hex"))

                res = self.dev.recv(1024)

                # 获取回应
                # reply = self.dev.read_reply()
                hexdump(res)

            except USBException as e:
                print e
                pass

            if not self.is_alive():
                print "设备未存活，下面打印最近的发包序列"
                print self.logger.dump_sequence()
                self.dev.reset()

    def is_alive(self):
        """
        如果设备存活返回 true
        :return:
        """
        ret = False
        try:
            self.dev.reset()
            ret = self.dev.is_alive()
        except:
            pass

        return ret

    def check_vuln(self, data):
        try:
            self.dev.send(data)
            reply = self.dev.read_reply()
        except:
            pass

        if not self.dev.is_alive():
            print "设备未存活，下面打印最近的发包序列"
            print data


class BulkFuzzer:

    def __init__(self, vid, pid, nomal_trans_conf, sample_path="", logseq_count=3, interval=0.01, workspace=""):
        """

        :param nomal_trans_conf: 交互序列配置文件，可以是目录，或者文件全路径
        :param logseq_count: 记录最近多少次的样本
        :param mutate_max_count: 变异的最大次数
        :param perseq_testcount: 一次循环对每个状态的变异测试
        """

        self.vid = vid
        self.pid = pid

        self.interval = interval
        self.dev = BulkPipe(vid=hex(vid), pid=hex(pid), interval=self.interval)

        # 从交互配置文件里面导入状态信息

        # state_data 是一个数组，每一项代码每个状态下可选数据集合
        self.state_data = []
        # 一个数组，每一项都是一个完整的交互序列
        self.trans = []
        #  如果是目录的话，就加载目录下的所有交互文件，然后合并每个状态下的交互过程， 用来后续 fuzz 时做种子
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

        self.workspace = workspace
        if self.workspace != "":
            if not os.path.exists(self.workspace):
                os.mkdir(self.workspace)
        else:
            self.workspace = os.path.abspath("")

        # 初始化测试序列日志队列，保存最近3次的测试序列
        self.logger = SequenceLogger(maxlen=logseq_count, log_dir=os.path.join(self.workspace, "logs"))

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
                        fuzz_seq['send'] = self.mutater.mutate(raw, maxlen=4000).encode("hex")

                    # 由于 python 指针传值的原因，需要重新生成对象，避免出现问题
                    # 生成完整的一个 测试序列
                    test_seqs = []
                    test_seqs += pre_seqs
                    test_seqs.append(fuzz_seq)

                    # 发送测试序列
                    if not self.send_to_target(test_seqs):

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

            # 如果服务器有欢迎消息，即欢迎消息非空，就先接收欢迎消息
            if self.welcome_msg:
                # 获取欢迎消息
                # data = p.recv(1024)
                data = self.dev.recv_until(self.welcome_msg)
                if self.welcome_msg not in data:
                    print "获取欢迎信息失败"
                    exit(0)
            else:
                sleep(0.2)

            # 发送前序数据包序列
            for seq in test_seqs[:-1]:
                self.dev.send(seq['send'].decode('hex'))
                # data = p.recv(1024)
                data = self.dev.recv_until(seq['recv'].decode('hex'))
                if seq['recv'].decode('hex') not in data:
                    print("*" * 20)
                    print("与服务器前序交互异常，下面是日志")
                    print("应该接受的回应：{}\n实际接收的回应：{}".format(seq['recv'], data.encode("hex")))
                    print("*" * 20)
            # 发送 fuzz 数据包， 即最后一个数据包
            self.dev.send(test_seqs[-1]['send'].decode('hex'))
            self.reset()
            self.fuzz_count += 1
            return True
        except Exception as e:
            print e
            self.exception_count += 1
            return False

    def reset(self):
        """
        重置设备，每次发送序列时，重置一次设备
        :return:
        """
        self.dev.reset()
        self.dev.ep_init()

    def is_alive(self):
        """
        判断目标是否存活
        :return: 如果存活返回 True, 否则返回 False
        """

        self.reset()
        if not self.dev.is_alive():
            return False

        # 首先检查端口是否开放
        data = ""
        count = 0

        while count < 3:
            try:
                # 如果服务器有欢迎消息，即欢迎消息非空，就先接收欢迎消息
                if self.welcome_msg:
                    # 获取欢迎消息
                    data = self.dev.recv_until(self.welcome_msg)
                    if self.welcome_msg not in data:
                        print "获取欢迎消息失败"
                        exit(0)
                else:
                    tran = self.trans[0]['trans']
                    for s in tran:
                        self.dev.send(s['send'].decode('hex'))
                        # data = p.recv(1024)
                        data = self.dev.recv_until(s['recv'].decode("hex"))

                        if s['recv'] not in data.encode('hex'):
                            print("except: {}, actal recv: {}".format(s['recv'], data.encode('hex')))
                            raise Exception("recv error")
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


class USBDeviceFuzzer:
    def __init__(self):
        pass


if __name__ == '__main__':
    # 0781:5591 ， 闪迪
    # 0951:1666 , 金士顿

    # fuzzer = CtrlFuzzer(0x0951, 0x1666)
    # fuzzer = MSCFuzzer(0x0781, 0x5591)
    #
    # fuzzer.fuzz()
    #
    # seqs = [u'5553424317000000342da031800011956526fd5c385c86638719036593b73f73',
    #         u'5553424315000000d847a3e580000595e8a134f80000000000000000000000',
    #         u'555342431300000038b26db380000d957f216565838434d808b25c59000000',
    #         u'5553424311000000da877bae80000b952252f44e51812790337d0000000000',
    #         u'555342430f000000b404c08880000d95ea7eb45394206369d6bccc90000000']
    #
    # for d in seqs:
    #     fuzzer.check_vuln(d)

    fuzzer = BulkFuzzer(vid=0x0781, pid=0x5591,
                        nomal_trans_conf="../../test/conf/sandisk.json")
    fuzzer.fuzz()

    #
    # for i in range(10):
    #     data = str(fuzz(APDU(CLA=0x80)))
    #     print "*" * 0x14
    #     hexdump(data)
