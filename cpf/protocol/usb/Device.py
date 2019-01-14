#!/usr/bin/python
# -*- coding: UTF-8 -*-

import usb.core
import usb.util
import usb.control
import sys
import time
from time import sleep

from Exceptions import *


class USBDevice:
    '''
    A simple USB Device base class.
    '''

    def __init__(self, vid, pid, timeout=500):
        '''
        @type    vid: string
        @param    vid: Vendor ID of device in hex
        @type    pid: string
        @param    pid: Product ID of device in hex
        @type    timeout: number
        @param    timeout: number of msecs to wait for reply
        '''

        self._vid = int(vid, 16)
        self._pid = int(pid, 16)
        self._timeout = int(timeout)
        if self._timeout < 100:
            self._timeout = 100

        self._device = usb.core.find(idVendor=self._vid, idProduct=self._pid)
        if self._device == None:
            raise USBException("设备 {}:{} 不存在".format(vid, pid))

        try:
            self._device.set_configuration()
        except usb.core.USBError as e:
            if e.errno == 16:  # Ignore "Resource Busy" error
                pass
            else:
                raise e

    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])

    def hex_dump(self, src, length=32):
        N = 0
        result = ''
        while src:
            s, src = src[:length], src[length:]
            hexa = ' '.join(["%02X" % ord(x) for x in s])
            s = s.translate(self.FILTER)
            result += "%04X   %-*s   %s\n" % (N, length * 3, hexa, s)
            N += length
        return result

    def reset(self):

        try:
            self._device.reset()
        except usb.core.USBError as e:
            raise USBException('Device could not be reset!')

        try:
            res = usb.control.get_status(self._device)
        except usb.core.USBError as e:
            raise USBException('Device not responding after reset!')

    def clear_stall(self, ep):

        try:
            usb.control.clear_feature(self._device, usb.control.ENDPOINT_HALT, ep)
        except usb.core.USBError as e:
            raise USBStalled('Could\'nt clear stall on ep 0x%0.2x!' % ep.bEndpointAddress)

    def is_alive(self):

        try:
            res = usb.control.get_status(self._device)
        except usb.core.USBError as e:
            return False

        return True


class BulkPipe(USBDevice):
    '''
    A simple interface to a USB Device bulk transfer pipe.
    '''

    def __init__(self, vid, pid, iface=0, timeout=500, interval=0.01):
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

        USBDevice.__init__(self, vid, pid, timeout)
        self._iface = int(iface)
        self.interval = interval

        self._epin = None
        self._epout = None

        # find bulk endpoints
        for c in self._device:
            for i in c:
                print("Interface: 0x%x 0x%x/0x%x/0x%x " % (
                    i.bInterfaceNumber, i.bInterfaceClass, i.bInterfaceSubClass, i.bInterfaceProtocol))
                if i.bInterfaceNumber == self._iface:
                    for ep in i:
                        print("Endpoint: 0x%x 0x%x " % (ep.bEndpointAddress, ep.bmAttributes))
                        if ep.bmAttributes == usb.ENDPOINT_TYPE_BULK:
                            if ep.bEndpointAddress & usb.ENDPOINT_DIR_MASK == usb.ENDPOINT_IN:
                                self._epin = ep
                            else:
                                self._epout = ep

        if not self._epin or not self._epout:
            raise USBException("Couldn't find bulk endpoints! (try different interface?)")
        # print("Using endpoints: 0x%x 0x%x " % (self._epin.bEndpointAddress, self._epout.bEndpointAddress))

        # claim interface from kernel
        try:
            self._device.detach_kernel_driver(self._iface)
        except usb.core.USBError as e:
            if e.errno == 2:  # "Entity not found"
                pass
            else:
                raise e

    def send(self, data):
        '''
        Send data on pipe
        
        @type    data: string
        @param    data: Data to send
        '''

        retry = 2
        while retry > 0:
            try:
                sleep(self.interval)
                self._epout.write(str(data), timeout=self._timeout)
                break
            except usb.core.USBError as e:
                retry -= 1
                if e.backend_error_code == -9:  # LIBUSB_ERROR_PIPE
                    self.clear_stall(self._epout)
                    sleep(0.1)
                sleep(0.001)

    def recv(self, size=1024):
        data = ""
        retry = 3
        while retry > 0:
            try:
                data = self._epin.read(size, timeout=self._timeout)
                break
            except usb.core.USBError as e:
                # print "端点读取异常: {}, {}".format(e, e.backend_error_code)
                retry -= 1
                if e.backend_error_code == -9:  # LIBUSB_ERROR_PIPE
                    self.clear_stall(self._epin)
                    sleep(0.01)

                sleep(0.001)
        string = ''.join(chr(byte) for byte in data)
        return string

    def recv_until(self, need, timeout=1):
        """
        读取到 need 返回所有读取的内容， 否则返回超时前读取的所有内容
        :param need: 需要的字符串
        :param timeout: 超时时间
        :return: 读取的内容
        """
        start = time.time()
        data = ""
        while need not in data:
            sleep(0.01)
            delta = time.time() - start
            if delta > timeout:
                return data
            data += self.recv(1024)
        return data

    def ep_init(self):
        """
        初始化 设备的 in, out 端点，保证后续可以正常读写
        :return:
        """
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


if __name__ == '__main__':
    from cpf.misc.utils import *

    bp = BulkPipe("0x0781", "0x5591")
    bp.reset()
    bp.ep_init()

    cmd = "5553424301000000c0f58fd780000b95ae3ebdf5af023a8b844d0000000000".decode("hex")
    bp.send(cmd)

    hexdump(bp.recv_until("555342".decode("hex"), timeout=3))

    # hexdump(bp.recv(1024))
    # hexdump(bp.recv(1024))

    # while True:
    #     try:
    #         print bt.receive(8)
    #         sleep(1)
    #     except:
    #         pass
