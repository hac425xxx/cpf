#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: BulkTransfer.py
@time: 2018/11/2 19:28
@desc:
"""
import usb.core
import usb.util
from time import sleep


class BulkTransfer:
    """
    实现 usb bluk 传输
    """

    def __init__(self, idVendor, idProduct, interface):
        """

        :param idVendor: usb设备的 vid
        :param idProduct: usb设备的 pid
        :param interface: 需要操作的 接口号
        """
        self.interface = interface

        # 获取设备，并且重置它
        self.dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        self.dev.reset()
        if self.dev is None:
            raise ValueError('Device not found')

        # 初始化 读、写端点
        self.epin = None
        self.epout = None

        # 通过遍历 dev 对象下的所有 interface ，找到 bluk 端点
        # 首先遍历 所有的配置符
        for c in self.dev:
            # 遍历配置描述符下的 interface
            for i in c:
                if i.bInterfaceNumber == self.interface:
                    # 然后在该接口下找 bluk 的 端点
                    for ep in i:
                        if ep.bmAttributes == usb.ENDPOINT_TYPE_BULK:
                            if ep.bEndpointAddress & usb.ENDPOINT_DIR_MASK == usb.ENDPOINT_IN:
                                self.epin = ep
                            else:
                                self.epout = ep

        # 如果找不全 输入、输出端点就退出
        if not self.epin or not self.epout:
            print("Couldn't find bulk endpoints! (try different interface?)")
            exit(1)

        try:
            self.dev.detach_kernel_driver(self.interface)
        except usb.core.USBError as e:
            if e.errno == 2:  # "Entity not found"
                pass
            else:
                raise e

    def send(self, data):
        self.epout.write(data)

    def recv(self, size):
        data = ""
        count = 0
        while True:
            # 出现异常，重试3次
            if count == 3:
                break

            try:
                data = self.epin.read(size, timeout=5000)
            except Exception as e:
                print(e)
                count += 1
                usb.control.clear_feature(self.dev, usb.control.ENDPOINT_HALT, self.epin)
                sleep(0.1)

        return data

    def is_dead(self):
        pass


if __name__ == '__main__':
    bt = BulkTransfer(0x0781, 0x5591, 0)
    bt.send("s" * 8)
    print(bt.recv(8))
