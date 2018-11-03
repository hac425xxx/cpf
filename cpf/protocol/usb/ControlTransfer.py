#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: ControlTransfer.py
@time: 2018/11/1 22:20
@desc:
"""
import usb.core
import usb.util
from cpf.protocol.Base import Base


class ControlTransfer(Base):
    """
    实现 usb 控制传输
    """

    def __init__(self, idVendor, idProduct):

        # find our device
        self.dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        self.dev.reset()

        if self.dev is None:
            raise ValueError('Device not found')

    # def __del__(self):
    #     print("释放掉usb设备")
    #     usb.util.dispose_resources(self.dev)

    def recv(self, size):
        pass

    def send(self, bmRequestType, bRequest, wValue, wIndex, data):
        """

        :param bmRequestType:
        :param bRequest:
        :param wValue:
        :param wIndex:
        :param data:
        :return:
        """
        self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data)

    def is_dead(self):
        try:
            res = usb.control.get_status(self.dev)
            print(res)
        except usb.core.USBError as e:
            if e.backend_error_code == -7:  # LIBUSB_ERROR_TIMEOUT
                print('传输超时')

            elif (e.backend_error_code == -4):  # LIBUSB_ERROR_NO_DEVICE
                print('设备已经断开')

            elif (e.backend_error_code == -3):  # LIBUSB_ERROR_ACCESS
                print('Device couldn\'t be accessed!')

            else:
                print(e)

            return True

        if res < 0 or res > 2:
            return True

        return False


if __name__ == '__main__':
    con = ControlTransfer(0x0781, 0x5591)

    try:
        con.dev.detach_kernel_driver(interface=0)
        usb.util.claim_interface(con.dev, interface=0)
    except:
        pass
    print(con.is_dead())
