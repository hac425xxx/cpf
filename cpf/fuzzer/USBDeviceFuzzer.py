#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import time
import random
import usb.core
import binascii
from scapy.packet import Raw, fuzz
from cpf.protocol.usb.CCID import *
from cpf.protocol.usb.QCDM import *
from cpf.protocol.usb.MTP import *
from cpf.protocol.usb.MSC import *


class CtrlFuzzer:
    def __init__(self, idVendor, idProduct, initq=0, initv=0, initvv=0):
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

    def fuzz(self):

        q = random.randint(self.initq, 0x100)
        v = random.randint(self.initv, 0x10)
        vv = random.randint(self.initvv, 0x10)
        i = random.randint(0, 0x10)

        if q == 3 and vv == 2 and i == 0:  # avoid SET_FEATURE TEST_MODE
            return

        ii = random.randint(0, 0x10)
        t = random.randint(0, 0x4)
        r = random.randint(0, 0x4)

        rt = (t << 5) | r
        r = q

        v = (v << 8) | vv
        i = (i << 8) | ii

        for size in (0, 10, 100, 4000):

            try:
                res = self.device.ctrl_transfer(rt & 0x80, r, v, i, bytearray().fromhex(u'ff' * size), timeout=250)
            except usb.core.USBError as e:
                if e.backend_error_code != -9 and e.backend_error_code != -1:  # ignore LIBUSB_ERROR_PIPE and LIBUSB_ERROR_IO
                    pass
            try:
                res = self.device.ctrl_transfer(rt | 0x80, r, v, i, size, timeout=250)
            except usb.core.USBError as e:
                if e.backend_error_code != -9 and e.backend_error_code != -1:  # ignore LIBUSB_ERROR_PIPE and LIBUSB_ERROR_IO
                    pass

            if i % 10 == 0:
                if not self.is_alive():
                    self.device.reset()
                    time.sleep(1)

    def is_alive(self):
        res = ""
        try:
            res = self.device.ctrl_transfer(0x80, 0, 0, 0, 2)
        except usb.core.USBError as e:

            if e.backend_error_code == -4:  # LIBUSB_ERROR_NO_DEVICE
                print "\nDevice not found!"
                sys.exit()

            if e.backend_error_code == -3:  # LIBUSB_ERROR_ACCESS
                print "\nAccess denied to device!"
                sys.exit()

            print "\nGET_STATUS returned error %i" % e.backend_error_code
            return False

        if len(res) != 2:
            print "\nGET_STATUS returned %u bytes: %s" % (len(res), binascii.hexlify(res))
            return False


class CCIDFuzzer:
    def __init__(self, vid, pid, timeout=2000):
        """

        :param vid:  设备的 vid , 类型 int
        :param pid: 设备的 pid , 类型 int
        :param timeout:
        """
        self.dev = CCIDDevice(vid=hex(vid), pid=hex(pid), timeout=timeout)
        self.dev.reset()

    def fuzz(self):
        while self.dev.is_alive():

            print "Sending command %u" % (self.dev.cur_seq() + 1)

            cmd = CCID(bSeq=self.dev.next_seq(), bSlot=0) / PC_to_RDR_XfrBlock() / fuzz(APDU(CLA=0x80))

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


class QCDMFuzzer:
    def __init__(self, vid, pid, iface=0):
        """

        :param vid:  设备的 vid , 类型 int
        :param pid: 设备的 pid , 类型 int
        :param iface:
        """
        self.dev = QCDMDevice(vid=hex(vid), pid=hex(pid), iface=iface)

    def fuzz(self):
        while self.dev.is_alive():

            cmd = QCDMFrame() / fuzz(Command()) / Raw(os.urandom(8))

            # avoid switching to downloader or test modes
            if cmd.code == 58 or cmd.code == 59:
                cmd.code = 0

            cmd.show2()
            print self.dev.hex_dump(str(cmd[Raw]))
            self.dev.send(str(cmd))
            res = self.dev.receive_response()

            if QCDMFrame in res:
                res.show()
                if Raw in res:
                    print self.dev.hex_dump(str(res[Raw]))
            else:
                print "No response to command!"
                print self.dev.hex_dump(str(res))


class MTPFuzzer:
    def __init__(self, vid, pid, wait=50, timeout=50):
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

        count = 1

        while self.dev.is_alive():
            print "测试：{} 次".format(count)
            count += 1
            trans = struct.unpack("I", os.urandom(4))[0]
            r = struct.unpack("H", os.urandom(2))[0]

            # 随机取一个 opcode
            opcode = OpCodes.items()[r % len(OpCodes)][1]

            if opcode == OpCodes["CloseSession"]:
                opcode = 0
            cmd = Container() / fuzz(
                Operation(OpCode=opcode, TransactionID=trans, SessionID=self.dev.current_session()))

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


class MSCFuzzer:
    def __init__(self, vid, pid, timeout=1200):
        self.dev = BOMSDevice(hex(vid), hex(pid), timeout=timeout)

        # make sure pipe is clear
        # 做一些清理操作
        self.dev.boms_reset()

        # Read Capacity to get blocksize
        cmd = MSCCBW() / SCSICmd() / ReadCapacity10()
        self.dev.send(cmd)
        reply = self.dev.read_reply()
        self.dev.check_status(reply)

        if Raw in reply and len(reply[Raw]) == 8:
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
        while self.dev is not None:
            try:
                opcode += 1
                test = 0
                while test < 100:
                    test += 1

                    r = struct.unpack("I", os.urandom(4))[0]
                    print "\nSending command %u with random value %x" % (self.dev.cur_tag() + 1, r)
                    cmd = MSCCBW(ReqTag=self.dev.next_tag(), ExpectedDataSize=r) / SCSICmd(OperationCode=opcode) / Raw(
                        os.urandom(r % 20))
                    # cmd.show2()
                    print self.dev.hex_dump(str(cmd))

                    try:
                        self.dev.send(cmd)
                        reply = self.dev.read_reply()
                    except USBException as e:
                        print "Exception: %s while processing command %u" % (e, self.dev.cur_tag())
                        self.dev.reset()
                    # do the test

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


class USBDeviceFuzzer:
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
