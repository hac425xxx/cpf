#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import click
import imp
import uuid
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
@click.option('--type', default="fuzz", help='运行模式,fuzz 或者 replay')
@click.option('--crash_path', default="fuzz", help='存放异常序列的文件路径')
@click.option('--callback_file', default="", help='存放 callback 函数实现的 py 文件，用于对变异数据进行修正，比如计算校验和')
def tcpfuzzer(host, port, conf, sample, lognum, interval, workspace, type, crash_path, callback_file):
    """ fuzz tcp服务 """

    if type == "fuzz":
        fuzzer = TCPFuzzer(host, port, nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum,
                           interval=interval,
                           workspace=workspace)

        callback = None
        try:

            # 如果 没有提供 callback_file 参数，尝试从 workspace/callback.py 提取 callback 函数
            if callback_file == "" and os.path.exists(os.path.join(workspace, "callback.py")):
                callback_file = os.path.join(workspace, "callback.py")

            if callback_file != "" and os.path.exists(callback_file):
                m = imp.load_source(str(uuid.uuid1()), callback_file)
                # 根据模块的 CALLBACK_FUNCTION 来找到 callback 的函数名
                func_name = getattr(m, "CALLBACK_FUNCTION")
                # 取出函数对象
                callback = getattr(m, func_name)
        except Exception as e:
            print "获取 callback 失败，异常为 {}".format(e)

        fuzzer.fuzz(callback=callback)
    else:
        try:
            fuzzer = TCPFuzzer(host, port, nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum,
                               interval=interval,
                               workspace=workspace)
            seqs = []
            with open(crash_path, "r") as fp:
                seqs = json.loads(fp.read())
            for seq in seqs:
                if fuzzer.check_vuln(seq):
                    ret = {
                        "crash": True,
                        "seq": seq
                    }
                    with open(os.path.join(workspace, "result.json"), "w") as fp:
                        fp.write(json.dumps(ret))

                    fuzzer.logger.exit_thread()
                    exit(0)
        except Exception as e:
            pass
        ret = {
            "crash": False,
        }
        with open(os.path.join(workspace, "result.json"), "w") as fp:
            fp.write(json.dumps(ret))

        fuzzer.logger.exit_thread()


@cli.command()
@click.option('--host', required=True, help='目标的IP地址')
@click.option('--port', type=int, required=True, help='目标的IP端口')
@click.option('--conf', type=click.Path(exists=True), required=True, help='正常交互序列配置文件的路径， 如果是目录的话就加载目录下的所有文件')
@click.option('--sample', default="", help='历史漏洞样本文件存放路径，用于辅助 fuzzer')
@click.option('--lognum', type=int, default=5, help='让 fuzzer 记录最近 lognum 次的发送序列，默认为 5')
@click.option('--interval', type=float, default=0.001, help='设置发包的时间间隔，默认 0.001 秒')
@click.option('--workspace', default="", help='当前fuzz的工作路径，路径下面保存一些运行时的信息')
@click.option('--type', default="fuzz", help='运行模式,fuzz 或者 replay')
@click.option('--crash_path', default="fuzz", help='存放异常序列的文件路径')
@click.option('--callback_file', default="", help='存放 callback 函数实现的 py 文件，用于对变异数据进行修正，比如计算校验和')
def udpfuzzer(host, port, conf, sample, lognum, interval, workspace, type, crash_path, callback_file):
    """ fuzz udp服务 """

    if type == "fuzz":
        fuzzer = UDPFuzzer(host, port, nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum,
                           interval=interval,
                           workspace=workspace)

        callback = None
        try:

            # 如果 没有提供 callback_file 参数，尝试从 workspace/callback.py 提取 callback 函数
            if callback_file == "" and os.path.exists(os.path.join(workspace, "callback.py")):
                callback_file = os.path.join(workspace, "callback.py")

            if callback_file != "" and os.path.exists(callback_file):
                m = imp.load_source(str(uuid.uuid1()), callback_file)
                # 根据模块的 CALLBACK_FUNCTION 来找到 callback 的函数名
                func_name = getattr(m, "CALLBACK_FUNCTION")
                # 取出函数对象
                callback = getattr(m, func_name)
        except Exception as e:
            print "获取 callback 失败，异常为 {}".format(e)

        fuzzer.fuzz(callback=callback)

    else:
        try:
            fuzzer = UDPFuzzer(host, port, nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum,
                               interval=interval,
                               workspace=workspace)
            seqs = []
            with open(crash_path, "r") as fp:
                seqs = json.loads(fp.read())
            for seq in seqs:
                if fuzzer.check_vuln(seq):
                    ret = {
                        "crash": True,
                        "seq": seq
                    }
                    with open(os.path.join(workspace, "result.json"), "w") as fp:
                        fp.write(json.dumps(ret))

                    fuzzer.logger.exit_thread()
                    exit(0)
        except Exception as e:
            pass

        ret = {
            "crash": False,
        }
        with open(os.path.join(workspace, "result.json"), "w") as fp:
            fp.write(json.dumps(ret))

        fuzzer.logger.exit_thread()


@cli.command()
@click.option('--device', default="/dev/ttyS0", help='串口设备路径，默认为 /dev/ttyS0')
@click.option('--baud', type=int, default=115200, help='波特率, 默认为 115200')
@click.option('--conf', type=click.Path(exists=True), required=True, help='正常交互序列配置文件的路径， 如果是目录的话就加载目录下的所有文件')
@click.option('--sample', default="", help='历史漏洞样本文件存放路径，用于辅助 fuzzer')
@click.option('--lognum', type=int, default=5, help='让 fuzzer 记录最近 lognum 次的发送序列，默认为 5')
@click.option('--interval', type=float, default=0.01, help='设置发包的时间间隔，默认 0.01 秒')
@click.option('--workspace', default="", help='当前fuzz的工作路径，路径下面保存一些运行时的信息')
@click.option('--type', default="fuzz", help='运行模式,fuzz 或者 replay')
@click.option('--crash_path', default="fuzz", help='存放异常序列的文件路径')
@click.option('--callback_file', default="", help='存放 callback 函数实现的 py 文件，用于对变异数据进行修正，比如计算校验和')
def serialfuzzer(device, baud, conf, sample, lognum, interval, workspace, type, crash_path, callback_file):
    """ fuzz 基于串口的服务 """

    if type == "fuzz":
        fuzzer = SerialFuzzer(device, baud,
                              nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum, interval=interval,
                              workspace=workspace)

        callback = None
        try:

            # 如果 没有提供 callback_file 参数，尝试从 workspace/callback.py 提取 callback 函数
            if callback_file == "" and os.path.exists(os.path.join(workspace, "callback.py")):
                callback_file = os.path.join(workspace, "callback.py")

            if callback_file != "" and os.path.exists(callback_file):
                m = imp.load_source(str(uuid.uuid1()), callback_file)
                # 根据模块的 CALLBACK_FUNCTION 来找到 callback 的函数名
                func_name = getattr(m, "CALLBACK_FUNCTION")
                # 取出函数对象
                callback = getattr(m, func_name)
        except Exception as e:
            print "获取 callback 失败，异常为 {}".format(e)

        fuzzer.fuzz(callback=callback)
    else:
        try:
            fuzzer = SerialFuzzer(device, baud,
                                  nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum, interval=interval,
                                  workspace=workspace)
            seqs = []
            with open(crash_path, "r") as fp:
                seqs = json.loads(fp.read())
            for seq in seqs:
                if fuzzer.check_vuln(seq):
                    ret = {
                        "crash": True,
                        "seq": seq
                    }
                    with open(os.path.join(workspace, "result.json"), "w") as fp:
                        fp.write(json.dumps(ret))

                    fuzzer.logger.exit_thread()
                    exit(0)
        except Exception as e:
            pass

        ret = {
            "crash": False,
        }
        with open(os.path.join(workspace, "result.json"), "w") as fp:
            fp.write(json.dumps(ret))

        fuzzer.logger.exit_thread()


@cli.command()
@click.option('--id', required=True, help='USB设备的标识符，格式 vid:pid, 比如 0x18d1:0x4ee2')
@click.option('--conf', default="", help='正常交互序列配置文件的路径， 如果是目录的话就加载目录下的所有文件')
@click.option('--sample', default="", help='历史漏洞样本文件存放路径，用于辅助 fuzzer')
@click.option('--lognum', type=int, default=5, help='让 fuzzer 记录最近 lognum 次的发送序列，默认为 5')
@click.option('--interval', type=float, default=0.01, help='设置发包的时间间隔，默认 0.01 秒')
@click.option('--workspace', default="", help='当前fuzz的工作路径，路径下面保存一些运行时的信息')
@click.option('--type', default="fuzz", help='运行模式,fuzz 或者 replay')
@click.option('--crash_path', default="fuzz", help='存放异常序列的文件路径')
@click.option('--usb_fuzz_type', default="ctrl", help='存放异常序列的文件路径')
@click.option('--callback_file', default="", help='存放 callback 函数实现的 py 文件，用于对变异数据进行修正，比如计算校验和')
def usbfuzzer(id, conf, sample, lognum, interval, workspace, type, crash_path, usb_fuzz_type, callback_file):
    """ fuzz usb设备 """

    vid = int(id.split(":")[0].strip(), 16)
    pid = int(id.split(":")[1].strip(), 16)

    if type == "fuzz":
        if usb_fuzz_type == "ctrl":
            fuzzer = CtrlFuzzer(vid, pid, workspace=workspace)
            fuzzer.fuzz()
        elif usb_fuzz_type == "bulk":
            fuzzer = BulkFuzzer(vid=vid, pid=pid, nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum,
                                interval=interval,
                                workspace=workspace)

            callback = None
            try:

                # 如果 没有提供 callback_file 参数，尝试从 workspace/callback.py 提取 callback 函数
                if callback_file == "" and os.path.exists(os.path.join(workspace, "callback.py")):
                    callback_file = os.path.join(workspace, "callback.py")

                if callback_file != "" and os.path.exists(callback_file):
                    m = imp.load_source(str(uuid.uuid1()), callback_file)
                    # 根据模块的 CALLBACK_FUNCTION 来找到 callback 的函数名
                    func_name = getattr(m, "CALLBACK_FUNCTION")
                    # 取出函数对象
                    callback = getattr(m, func_name)
            except Exception as e:
                print "获取 callback 失败，异常为 {}".format(e)

            fuzzer.fuzz(callback=callback)
    else:
        try:
            if usb_fuzz_type == "ctrl":
                fuzzer = CtrlFuzzer(vid, pid, workspace=workspace)
            elif usb_fuzz_type == "bulk":
                fuzzer = BulkFuzzer(vid=vid, pid=pid, nomal_trans_conf=conf, sample_path=sample, logseq_count=lognum,
                                    interval=interval,
                                    workspace=workspace)

            seqs = []
            with open(crash_path, "r") as fp:
                seqs = json.loads(fp.read())
            for seq in seqs:
                if fuzzer.check_vuln(seq):
                    ret = {
                        "crash": True,
                        "seq": seq
                    }
                    with open(os.path.join(workspace, "result.json"), "w") as fp:
                        fp.write(json.dumps(ret))

                    fuzzer.logger.exit_thread()
                    exit(0)
        except Exception as e:
            print e

        ret = {
            "crash": False,
        }

        with open(os.path.join(workspace, "result.json"), "w") as fp:
            fp.write(json.dumps(ret))

        # 退出线程
        fuzzer.logger.exit_thread()


if __name__ == '__main__':
    cli()

"""
测试 ftp
fuzz.py tcpfuzzer --host 192.168.245.131 --port 21 --conf /fuzzer/test/conf/floatftp --interval 0

测试 bulk fuzzer
fuzz.py usbfuzzer --type fuzz --usb_fuzz_type bulk  --id 0x0781:0x5591 --workspace /tmp/sandisk --conf /fuzzer/test/conf/sandisk/conf/sandisk.json
"""
