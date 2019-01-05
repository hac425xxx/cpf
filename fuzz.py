#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import click
from cpf.fuzzer.TCPFuzzer import TCPFuzzer
from cpf.fuzzer.UDPFuzzer import UDPFuzzer
from cpf.fuzzer.SerialFuzzer import SerialFuzzer
from cpf.fuzzer.USBDeviceFuzzer import *

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def cli():
    pass


@cli.command()
@click.option('--host', required=True, help='目标的IP地址')
@click.option('--port', type=int, required=True, help='目标的IP端口')
@click.option('--conf', type=click.Path(exists=True), required=True, help='存放正常交互流量的路径， 如果是目录的话就加载目录下的所有文件')
@click.option('--sample', default="", help='历史漏洞样本文件存放路径，用于辅助 fuzzer')
@click.option('--lognum', type=int, default=5, help='让 fuzzer 记录最近 lognum 次的发送序列，默认为 5')
@click.option('--interval', type=float, default=0.001, help='设置发包的时间间隔，默认 0.001 秒')
@click.option('--workspace', default="", help='当前fuzz的工作路径，路径下面保存一些运行时的信息')
def tcpfuzzer(host, port, conf, sample, lognum, interval, workspace):
    """ fuzz tcp服务 """

    fuzzer = TCPFuzzer(host, port, nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum, interval=interval,
                       workspace=workspace)
    fuzzer.fuzz()


@cli.command()
@click.option('--host', required=True, help='目标的IP地址')
@click.option('--port', type=int, required=True, help='目标的IP端口')
@click.option('--conf', type=click.Path(exists=True), required=True, help='正常交互序列配置文件的路径， 如果是目录的话就加载目录下的所有文件')
@click.option('--sample', default="", help='历史漏洞样本文件存放路径，用于辅助 fuzzer')
@click.option('--lognum', type=int, default=5, help='让 fuzzer 记录最近 lognum 次的发送序列，默认为 5')
@click.option('--interval', type=float, default=0.001, help='设置发包的时间间隔，默认 0.001 秒')
@click.option('--workspace', default="", help='当前fuzz的工作路径，路径下面保存一些运行时的信息')
def udpfuzzer(host, port, conf, sample, lognum, interval, workspace):
    """ fuzz udp服务 """

    fuzzer = UDPFuzzer(host, port, nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum, interval=interval,
                       workspace=workspace)
    fuzzer.fuzz()


@cli.command()
@click.option('--device', default="/dev/ttyS0", help='串口设备路径，默认为 /dev/ttyS0')
@click.option('--baud', type=int, default=115200, help='波特率, 默认为 115200')
@click.option('--conf', type=click.Path(exists=True), required=True, help='正常交互序列配置文件的路径， 如果是目录的话就加载目录下的所有文件')
@click.option('--sample', default="", help='历史漏洞样本文件存放路径，用于辅助 fuzzer')
@click.option('--lognum', type=int, default=5, help='让 fuzzer 记录最近 lognum 次的发送序列，默认为 5')
@click.option('--interval', type=float, default=0.01, help='设置发包的时间间隔，默认 0.01 秒')
@click.option('--workspace', default="", help='当前fuzz的工作路径，路径下面保存一些运行时的信息')
def serialfuzzer(device, baud, conf, sample, lognum, interval, workspace):
    """ fuzz 基于串口的服务 """

    fuzzer = SerialFuzzer(device, baud,
                          nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum, interval=interval,
                          workspace=workspace)
    fuzzer.fuzz()


@cli.command()
@click.option('--id', required=True, help='USB设备的标识符，格式 vid:pid, 比如 0x18d1:0x4ee2')
@click.option('--workspace', default="", help='当前fuzz的工作路径，路径下面保存一些运行时的信息')
def usbfuzzer(id, workspace):
    """ fuzz usb设备 """

    vid = int(id.split(":")[0].strip(), 16)
    pid = int(id.split(":")[1].strip(), 16)

    # print "{}:{}".format(hex(vid), hex(pid))

    fuzzer = CtrlFuzzer(vid, pid, workspace=workspace)
    fuzzer.fuzz()


if __name__ == '__main__':
    cli()

"""
测试 ftp
fuzz.py tcpfuzzer --host 192.168.245.131 --port 21 --conf /fuzzer/test/conf/floatftp --interval 0

"""