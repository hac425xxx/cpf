#!/usr/bin/env python
# encoding: utf-8

"""
@author: hac425
@file: p2.py
@time: 2018/11/1 21:45
@desc:
"""
import uuid


def process():
    print("from p2")


if __name__ == '__main__':
    import importlib
    import imp

    # p1 = importlib.import_module("/fuzzer/test/plugins/p1.py")
    m = imp.load_source(str(uuid.uuid1()), "/fuzzer/test/plugins/p1.py")
    func_name = getattr(m, "CALLBACK_FUNCTION")
    func = getattr(m, func_name)
    print func("ssssssssss")
