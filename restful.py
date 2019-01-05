#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import sqlite3
from flask import Flask, jsonify, request
from flask import g
import zipfile
import subprocess
import uuid
import threading
import base64
import signal
import os
import time
from time import sleep
import json
import datetime

DATABASE = '/tmp/xxxxx.db'
# task_id:thread obj, 用来表示任务对应的线程
THREADS = {}
app = Flask(__name__)


def connect_db():
    return sqlite3.connect(DATABASE)


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/query', methods=['GET'])
def query():
    """
    获取所有数据库里面的信息
    :return:
    """
    data = []
    infos = g.db.execute("select * from project_information")
    for i in infos:
        info = {}
        info['task_id'] = i[0]
        info['project_name'] = i[1]
        info['pid'] = i[2]
        info['start_time'] = i[3]
        info['crash_sequence'] = i[4]
        info['cmdline'] = i[5]
        info['workspace'] = i[6]
        # 计算出运行时间，单位为 秒
        info['runtime'] = str(get_delta(int(info['start_time'])))
        data.append(info)

    ret = {
        "result": "successful",
        "data": data
    }
    return jsonify(ret)


@app.route('/status/<task_id>/', methods=['GET'])
def status(task_id):
    i = g.db.execute("select * from project_information where task_id='{}'".format(task_id)).fetchone()
    info = {}
    info['task_id'] = i[0]
    info['project_name'] = i[1]
    info['pid'] = i[2]
    info['start_time'] = i[3]
    info['crash_sequence'] = i[4]
    info['cmdline'] = i[5]
    info['workspace'] = i[6]
    info['status'] = i[7]
    # 计算出运行时间，单位为 秒
    info['runtime'] = str(get_delta(int(info['start_time'])))
    info['runtime_log'] = os.path.join(info['workspace'], "runtime.json")

    if info['crash_sequence'] != "":
        info['crash_sequence'] = json.loads(base64.decodestring(info['crash_sequence']))
        ret = {
            "result": "successful",
            "project_info": info,
            "is_run": False
        }
        return jsonify(ret)

    # 从 运行日志文件中加载数据
    if os.path.exists(info['runtime_log']):
        runtime_log = {}
        with open(info['runtime_log'], "r") as fp:
            runtime_log = json.loads(fp.read())

        # runtime_log['is_run'] = False
        runtime_log['fuzz_time'] = info['runtime']

        if info['crash_sequence'] == "" and runtime_log.has_key('crash_sequence'):
            crash_seqs = base64.encodestring(json.dumps(runtime_log['crash_sequence']))

            g.db.execute("UPDATE project_information SET crash_sequence='{}',status='dead' where task_id='{}'".format(
                crash_seqs, info['task_id']))
            g.db.commit()

        ret = {
            "result": "successful",
            "runtime": runtime_log,
            "project_info": info,
            "is_run": True
        }
    else:
        ret = {
            "result": "fail",
            "msg": u"实时日志文件加载失败",
            "project_info": info
        }
    return jsonify(ret)


@app.route('/stop/<task_id>/', methods=['GET'])
def stop(task_id):
    i = g.db.execute("select * from project_information where task_id='{}'".format(task_id)).fetchone()
    pid = int(i[2])
    # print kill(pid)

    workspace = i[6]
    log = os.path.join(workspace, "runtime.json")

    runtime = {}
    with open(log, "r") as fp:
        runtime = json.loads(fp.read())

    runtime['is_run'] = False
    with open(log, "w") as fp:
        fp.write(json.dumps(runtime))

    cmd = "ps -ef | grep python | grep %s | awk  '{print $2}' |xargs  kill -9" % (task_id)
    os.system(cmd)
    ret = {
        "result": "successful"
    }

    g.db.execute("UPDATE project_information SET status='dead' where task_id='{}'".format(task_id))
    g.db.commit()
    return jsonify(ret)


@app.route('/create', methods=['POST'])
def create():
    """

    {
        "type":"",
        "project_name":"",
        "max_run_time":0,
        "arguments":""
    }

    创建一个任务， 返回 task id
    :return:
    """
    if not request.json:
        return jsonify({"result": "fail", "msg": u"数据错误"})

    # print request.json

    project_name = request.json['project_name']
    arguments = request.json['arguments']
    type = request.json['type']

    task_id = str(uuid.uuid1())
    workdir = os.path.dirname(__file__)

    dir = "data/{}_{}_{}".format(type, project_name, task_id)
    workspace = os.path.join(workdir, dir)
    os.mkdir(workspace)

    cmdline = "python -u fuzz.py {} --workspace {}".format(arguments, workspace)

    cmd = Command(cmdline, workdir)

    THREADS[task_id] = cmd
    pid = cmd.run()

    # thread = threading.Thread(target=execute, args=(cmdline, workdir))
    # thread.start()

    insert(task_id, project_name, pid, int(time.time()), "", cmdline, workspace, "runing")

    ret = {
        "result": "successful",
        "task_id": task_id
    }
    return jsonify(ret)


@app.route('/update', methods=['POST'])
def update():
    """
    更新 运行日志文件
    {
        "task_id": "",
        "fuzz_count": "",
        "fuzz_result": "",
        "crash_sequence":""
    }
    :return:
    """
    if not request.json:
        return jsonify({"result": "fail", "msg": u"数据错误"})

    task_id = request.json['task_id']
    i = g.db.execute("select * from project_information where task_id='{}'".format(task_id)).fetchone()
    runtime_log = i[6]

    log = {}
    log['fuzz_count'] = request.json['fuzz_count']
    log['is_run'] = request.json['fuzz_result']
    log['crash_sequence'] = request.json['crash_sequence']

    with open(runtime_log, "w") as fp:
        fp.write(json.dumps(log))

    return jsonify({"result": "successful"})


@app.route('/upload', methods=['POST'])
def upload():
    """
    上传的文件应该是压缩文件, 解压缩到 data 目录下，目录名为 文件名+ts
    :return:
    """
    f = request.files['file']
    tmp_path = os.path.join("/tmp", f.filename)
    f.save(tmp_path)
    data_dir = get_data_dir()

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    save_path = "{}_{}".format(os.path.join(data_dir.encode("utf-8"), f.filename.split(".")[0]), int(time.time()))
    unzip_file(tmp_path, save_path)

    return jsonify({"result": "successful"})


class Command(object):
    def __init__(self, cmd, workdir):
        self.cmd = cmd
        self.process = None
        self.thread = None
        self.workdir = workdir

    def run(self):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True, cwd=self.workdir)
            self.process.communicate()

        self.thread = threading.Thread(target=target)

        self.thread.start()

        while not self.process:
            sleep(0.1)
        return self.process.pid


def execute(cmd, cwd):
    process = subprocess.Popen(cmd, shell=True, cwd=cwd)
    process.communicate()


def get_data_dir():
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, "data")
    return os.path.abspath(path)


def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS project_information( task_id TEXT PRIMARY KEY, project_name TEXT, pid TEXT, start_time TEXT, crash_sequence TEXT, cmdline TEXT, workspace TEXT,status TEXT)')
    cursor.close()
    conn.commit()


def unzip_file(zipfilename, unziptodir):
    """
    解压 zip 文件到目录
    :param zipfilename:  zip 文件路径
    :param unziptodir:  解压后的内容存放的路径， 如果目录不存在会新建目录
    :return:
    """
    if not os.path.exists(unziptodir): os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir): os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


def insert(task_id, project_name, pid, start_time, crash_sequence, cmdline, workspace, status):
    """
    往 project_information 插入一条记录
    :param task_id:
    :param project_name:
    :param pid:
    :param start_time:
    :param crash_sequence:
    :param cmdline:
    :param runtime_log:
    :return:
    """
    sql = ''' INSERT INTO project_information 
(task_id, project_name, pid, start_time, crash_sequence, cmdline, workspace, status) 
VALUES 
(:task_id, :project_name, :pid, :start_time, :crash_sequence, :cmdline, :workspace,:status)'''
    g.db.execute(sql, {'task_id': task_id, 'project_name': project_name, 'pid': pid, "start_time": start_time,
                       "crash_sequence": crash_sequence, "cmdline": cmdline, "workspace": workspace, "status": status})
    g.db.commit()

    return True


def get_delta(ts):
    """
    返回从 ts 到 now 经过的 秒数
    :param ts:  时间戳
    :return:
    """
    old = datetime.datetime.fromtimestamp(ts)
    now = datetime.datetime.now()
    delta = (now - old)
    return delta.seconds


def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def kill(pid):
    try:
        a = os.kill(pid, signal.SIGTERM)
        # a = os.kill(pid, signal.9) #　与上等效
        return '已杀死pid为%s的进程,　返回值是:%s' % (pid, a)
    except OSError, e:
        return '没有如此进程!!!'


if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", debug=True)
