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


class CtrlFuzzer:
    def __init__(self, idVendor, idProduct, initq=0, initv=0, initvv=0, workspace=""):
        """

        :param idVendor: 设备的 idVendor ， int
        :param idProduct: 设备的 idProduct ， int
        :param initq:
        :param initv:
        :param initvv:
        """
        self.device = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        self.initq = initq
        self.initv = initv
        self.initvv = initvv
        self.mutater = Mutater()
        self.fuzz_count = 0

        self.workspace = workspace
        # 工作目录用于存放运行日志，crash, 后续可能用于记录 log....
        # 目录不存在就创建一个
        self.workspace = workspace
        if self.workspace != "":
            if not os.path.exists(self.workspace):
                os.mkdir(self.workspace)
        self.logger = SequenceLogger(logs=os.path.join(self.workspace, "logs"))

    def fuzz(self):

        while True:

            self.fuzz_count += 1

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

                self.device.reset()
                time.sleep(1)

    def check(self, packets=[]):
        for data in packets:
            data = data.decode('hex')
            bmRequestType = int(data[0].encode("hex"), 16)
            bRequest = int(data[1].encode("hex"), 16)
            wValue = int(data[2:4].encode("hex"), 16)
            wIndex = int(data[4:6].encode("hex"), 16)

            try:
                self.logger.add_to_queue(data.encode("hex"))
                res = self.device.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data[6:], timeout=250)
            except usb.core.USBError as e:
                if e.backend_error_code != -9 and e.backend_error_code != -1:  # ignore LIBUSB_ERROR_PIPE and LIBUSB_ERROR_IO
                    pass

            if not self.is_alive():
                seqs = self.logger.dump_sequence()
                self.device.reset()
                time.sleep(1)

    def is_alive(self):
        res = ""
        try:
            res = self.device.ctrl_transfer(0x80, 0, 0, 0, 2)
        except usb.core.USBError as e:

            if e.backend_error_code == -4:  # LIBUSB_ERROR_NO_DEVICE
                # print "\nDevice not found!"
                return False

            if e.backend_error_code == -3:  # LIBUSB_ERROR_ACCESS
                # print "\nAccess denied to device!"
                return False

            # print "\nGET_STATUS returned error %i" % e.backend_error_code
            return False

        if len(res) != 2:
            # print "\nGET_STATUS returned %u bytes: %s" % (len(res), binascii.hexlify(res))
            return False

        return True


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
            res = self.dev.receive()

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
        self.logger = SequenceLogger()
        # 初始化 pipe
        self.dev.boms_reset()

        # 利用 ReadCapacity 指令，获取设备的信息
        cmd = MSCCBW() / SCSICmd() / ReadCapacity10()
        self.dev.send(cmd)
        reply = self.dev.read_reply()
        self.dev.check_status(reply)

        if Raw in reply and len(reply[Raw]) == 8:
            # 获取到 一些设备的信息，
            data = str(reply[Raw])
            max_lba = struct.unpack(">I", data[:4])[0]
            block_size = struct.unpack(">I", data[4:])[0]
        else:
            reply.show()
            sys.exit()

        print "Device is %uMb, max LBA is %x and blocksize is %x" % (
            round(float(max_lba * block_size) / 1048576), max_lba, block_size)

    def fuzz(self):

        opcode = 0x95
        while True:
            try:
                opcode += 1
                test = 0
                while test < 100:
                    test += 1

                    # 生成测试数据
                    r = struct.unpack("I", os.urandom(4))[0]
                    cmd = MSCCBW(ReqTag=self.dev.next_tag(), ExpectedDataSize=r) / SCSICmd(OperationCode=opcode) / Raw(
                        os.urandom(r % 20))

                    # 发送到目标
                    try:
                        # 添加到日志
                        self.logger.add_to_queue(str(cmd).encode("hex"))
                        self.dev.send(cmd)
                        reply = self.dev.read_reply()
                    except USBException as e:
                        self.dev.reset()

                    # display any data in reply
                    if Raw in reply and len(reply) > 0:
                        print self.dev.hex_dump(str(reply[Raw]))

                    # check CSW
                    ok = self.dev.check_status(reply)
                    if len(reply) == 0:
                        print "No response to command %u!" % self.dev.cur_tag()

                    # monitor target
                    if test % 10 == 0:
                        if not self.dev.is_alive():
                            print "Device not responding, resetting!"
                            self.dev.reset()

            except USBException as e:
                print "Exception: %s in command loop, resetting!" % e
                self.dev.reset()

            if not self.dev.is_alive():
                print "设备未存活，下面打印最近的发包序列"
                print self.logger.dump_sequence()


class USBDeviceFuzzer:
    def __init__(self):
        pass


if __name__ == '__main__':
    # 0781:5591

    fuzzer = CtrlFuzzer(0x0951, 0x1666)

    #  18d1:4ee2
    # fuzzer = MTPFuzzer(0x0951, 0x1666)

    # fuzzer.check([u'06013a000000343400344b34343434', u'8006c0810000343434343434c200e9260134',
    #               u'80060100000034343434343434000034'])

    fuzzer.fuzz()
    #
    # for i in range(10):
    #     data = str(fuzz(APDU(CLA=0x80)))
    #     print "*" * 0x14
    #     hexdump(data)
