#!/usr/bin/env python

from Exceptions import *
from SCSI import *
from Device import BulkPipe

from scapy.fields import *
from scapy.packet import Packet, Raw, bind_layers

import usb.control


class MSCCBW(Packet):
    name = "USB MSC Command Block Wrapper "
    fields_desc = [XIntField("Magic", 0x55534243),
                   LEIntField("ReqTag", 0),
                   LEIntField("ExpectedDataSize", 8),
                   ByteEnumField("Flags", 0x80, {0x80: "IN", 0: "OUT"}),
                   ByteField("LUN", 0),
                   ByteField("SCSICmdLength", None)]

    BLOCK_SIZE = 0x200

    def build(self):
        # update fields that depend on values in SCSI layer
        if SCSICmd in self:
            scsicmd = self[SCSICmd].payload
            if scsicmd.default_fields.has_key("AllocationLength"):
                self.overloaded_fields.update({"ExpectedDataSize": scsicmd.AllocationLength})
            if scsicmd.default_fields.has_key("TransferLength"):
                self.overloaded_fields.update({"ExpectedDataSize": scsicmd.TransferLength * self.BLOCK_SIZE})
        return Packet.build(self)

    def post_build(self, p, pay):
        # default value for SCSI Command Block length
        if self.SCSICmdLength is None:
            self.SCSICmdLength = len(pay)
            p = p[:-1] + struct.pack("B", len(pay))
        # pad SCSI Command Blocks to 16 bytes
        if len(pay) < 16:
            pay += '\x00' * (16 - len(pay))
        return p + pay

    def default_payload_class(self, payload):
        return SCSICmd


bind_layers(MSCCBW, SCSICmd)


class MSCCSW(Packet):
    name = "USB MSC Command Status Wrapper "
    fields_desc = [XIntField("Magic", 0x55534253),
                   LEIntField("ReqTag", 0),
                   LEIntField("DataResidue", 0),
                   XByteField("ReqStatus", 0)]


class BOMSDevice(BulkPipe):

    def __init__(self, vid, pid, iface=0, timeout=500):

        '''
        @type    vid: string
        @param    vid: Vendor ID of device in hex
        @type    pid: string
        @param    pid: Product ID of device in hex
        @type    iface: number
        @param    iface: Device Interface to use
        @type    timeout: number
        @param    timeout: number of msecs to wait for reply
        '''

        BulkPipe.__init__(self, vid, pid, iface, timeout)

        self._tag = 0

    def cur_tag(self):

        return self._tag

    def next_tag(self):

        self._tag = (self._tag + 1) % 0xffffffff
        return self._tag

    def boms_reset(self):

        try:
            # issue Bulk-Only Mass Storage Reset
            bmRequestType = usb.util.build_request_type(
                usb.util.CTRL_OUT,
                usb.util.CTRL_TYPE_CLASS,
                usb.util.CTRL_RECIPIENT_INTERFACE)

            self._device.ctrl_transfer(
                bmRequestType=bmRequestType,
                bRequest=0x0ff,
                wIndex=self._iface)

            # clear STALL condition
            self.clear_stall(self._epin)
            self.clear_stall(self._epout)

        except usb.core.USBError as e:
            print "%s in boms_reset()!" % e

    def reset(self):

        self.boms_reset()
        BulkPipe.reset(self)

    def read_reply(self, length=1024):
        data = ""
        try:
            res = "."
            while len(res) > 0:
                if len(res) > 12 and res[-13:-9] == "USBS":
                    break
                res = self.recv(length)
                data += res
        except USBException as e:
            print "%s in read_reply(), resetting!" % e
            self.boms_reset()

        if len(data) < 13:
            return Raw(data)

        if len(data) == 13:
            return MSCCSW(data)

        return MSCCSW(data[-13:]) / Raw(data[:-13])

    def check_status(self, packets):

        if len(packets) == 0:
            return False

        # try to get CSW if we haven't yet
        if MSCCSW not in packets:
            csw = self.read_reply()
            if MSCCSW not in csw:
                print "No CSW for request %u!" % self.cur_tag()
                return False
        else:
            csw = packets[MSCCSW]

        if csw.Magic != 0x55534253:
            print "Invalid magic '%s' in CSW for request %u!" % (str(csw.Magic), self._tag)
            packets.show()
            return False

        if csw.ReqTag != self.cur_tag():
            print "Tag mismatch %u != %u in CSW!" % (csw.ReqTag, self.cur_tag())
            # return False

        if csw.ReqStatus == 2:
            print "Phase error in CSW for request %s!" % str(csw.ReqTag)
            self.boms_reset()
            return True

        if csw.ReqStatus == 1:
            print "Command failed for request %s!" % str(csw.ReqTag)
            self.send(MSCCBW(ReqTag=self.next_tag()) / RequestSense())
            reply = self.read_reply()
            # reply.show() # sense data
            if self.check_status(reply):
                return True
            return False

        if csw.ReqStatus == 0:
            return True

        print "Unknown Status in CSW for request %s!" % str(csw.ReqTag)
        csw.show()
        return False

    def is_alive(self):

        if not BulkPipe.is_alive(self):
            return False

        try:
            self.send(MSCCBW(ReqTag=self.next_tag()) / Read10())
            reply = self.read_reply()
            print "***" * 15
            hexdump(reply)
            print "***" * 15
        except USBException as e:
            return False

        return self.check_status(reply)


if __name__ == '__main__':
    from cpf.misc.utils import *

    bp = BOMSDevice("0x0781", "0x5591")
    bp.reset()

    # 5553424301000000f2f58fd780000b95ae3ebdf5d2cd4937844e0000000000
    cmd = "5553424301000000c0f58fd780000b95ae3ebdf5af023a8b844d0000000000".decode("hex")
    bp.send(cmd)

    hexdump(bp.recv_until("555342".decode("hex"), timeout=3))
