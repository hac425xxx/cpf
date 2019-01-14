#!/usr/bin/env python
# encoding: utf-8

import usb.core
import usb.util

import usb.backend.libusb1
from time import sleep

# find our device
dev = usb.core.find(idVendor=0x0781, idProduct=0x5591)
# dev.reset()

# was it found?
if dev is None:
    raise ValueError('Device not found')

try:
    dev.detach_kernel_driver(interface=0)
    usb.util.claim_interface(dev, interface=0)
except:
    pass

ep_in = dev[0][0, 0][0]
ep_out = dev[0][0, 0][1]
#
# # ep_out.write("40f1f200f3000000".decode("hex"))
#


while True:
    try:
        print ep_in.read(8)
    except:
        pass

    sleep(0.5)

# 发送原始的 控制报文
# dev.ctrl_transfer(0x40, 0xbb, 0xccdd, 0xeeff, "ssssssss")

# 通过发送原始报文获取描述符
dev.ctrl_transfer(0x80, 0x06, 0x0100, 0x0000)

# usb.util.dispose_resources(dev)

# dev.intr_write(dev, ep_out, itf, "ssss", 2000)
