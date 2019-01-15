#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import sqlite3
from flask import Flask, jsonify, request, send_from_directory
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

    ts = int(i[3])
    time_local = time.localtime(ts)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    info['start_time'] = dt
    info['crash_sequence'] = i[4]
    info['cmdline'] = i[5]
    info['workspace'] = i[6]
    info['status'] = i[7]
    # 计算出运行时间，单位为 秒
    info['runtime'] = str(get_delta(ts))
    info['runtime_log'] = os.path.join(info['workspace'], "runtime.json")

    if info['crash_sequence'] != "":
        info['crash_sequence'] = json.loads(base64.decodestring(info['crash_sequence']))
        # ret = {
        #     "result": "successful",
        #     "project_info": info,
        #     "is_run": False
        # }
        # return jsonify(ret)

    # 从 运行日志文件中加载数据
    if os.path.exists(info['runtime_log']):
        runtime_log = {}
        # 加载日志文件中的日志
        with open(info['runtime_log'], "r") as fp:
            runtime_log = json.loads(fp.read())

        if not runtime_log.has_key('fuzz_time'):
            runtime_log['fuzz_time'] = info['runtime']

        if info['crash_sequence'] == "" and runtime_log.has_key('crash_sequence'):
            crash_seqs = base64.encodestring(json.dumps(runtime_log['crash_sequence']))
            with open(info['runtime_log'], "w") as fp:
                fp.write(json.dumps(runtime_log))

            g.db.execute("UPDATE project_information SET crash_sequence='{}',status='dead' where task_id='{}'".format(
                crash_seqs, info['task_id']))
            g.db.commit()

        if runtime_log.has_key('crash_sequence'):
            runtime_log['crash_sequence'] = ""
        ret = {
            "result": "successful",
            "runtime": runtime_log,
            "project_info": info
        }
    else:
        ret = {
            "result": "fail",
            "msg": u"实时日志文件加载失败",
            "project_info": info,
            "status": "alive"
        }
        if not check_pid(info['pid']):
            ret['status'] = "dead"

    return jsonify(ret)


@app.route('/connect', methods=['GET'])
def connect():
    return jsonify({"status": "ok"})


@app.route('/stop/<task_id>/', methods=['GET'])
def stop(task_id):
    i = g.db.execute("select * from project_information where task_id='{}'".format(task_id)).fetchone()
    pid = int(i[2])
    # print kill(pid)

    ts = int(i[3])
    workspace = i[6]
    log = os.path.join(workspace, "runtime.json")

    if not os.path.exists(log):
        ret = {
            "result": "fail"
        }
        return jsonify(ret)

    runtime = {}
    with open(log, "r") as fp:
        runtime = json.loads(fp.read())

    runtime['is_run'] = False
    runtime['fuzz_time'] = str(get_delta(ts))
    with open(log, "w") as fp:
        fp.write(json.dumps(runtime))

    cmd = "ps -ef | grep python | grep %s | awk  '{print $2}' |xargs  kill -9" % (workspace)
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
    创建一个任务， 返回 task id
    :return:
    """
    if not request.json:
        return jsonify({"result": "fail", "msg": u"数据错误"})

    # print request.json
    cmdline = ""
    project_name = request.json['project_name']
    type = request.json['type']
    workspace = request.json['workspace']

    task_id = str(uuid.uuid1())
    workdir = os.path.dirname(__file__)

    # 是否提供 样本库
    has_sample = False
    sample_path = os.path.join(workspace, "sample")  # sample/ 下面存放历史漏洞样本库
    if not os.path.exists(sample_path) or is_empty(sample_path):
        sample_path = ""

    if type == "tcp":
        t1 = request.json['t1']
        t2 = request.json['t2']
        conf_path = os.path.join(workspace, "conf")
        speed = request.json['speed']
        cmdline = "python -u fuzz.py tcpfuzzer --host {} --port {} --conf {} --workspace {} --interval {}".format(
            t1,
            t2,
            conf_path,
            workspace,
            speed)

    elif type == "udp":
        t1 = request.json['t1']
        t2 = request.json['t2']
        conf_path = os.path.join(workspace, "conf")
        speed = request.json['speed']
        cmdline = "python -u fuzz.py udpfuzzer --host {} --port {} --conf {} --workspace {} --interval {}".format(
            t1,
            t2,
            conf_path,
            workspace,
            speed)

    elif type == "serial":
        t1 = request.json['t1']
        t2 = request.json['t2']
        conf_path = os.path.join(workspace, "conf")
        speed = request.json['speed']
        cmdline = "python -u fuzz.py serialfuzzer --device {} --baud {} --conf {} --workspace {} --interval {}".format(
            t1,
            t2,
            conf_path,
            workspace,
            speed)
    else:
        t1 = request.json['t1']
        t2 = request.json['t2']
        id = "{}:{}".format(t1, t2)

        usb_fuzz_type = request.json['usb_fuzz_type']

        if usb_fuzz_type == "ctrl":
            cmdline = "python -u fuzz.py usbfuzzer --id {} --workspace {}".format(
                id,
                workspace)
        elif usb_fuzz_type == "bulk":
            conf_path = os.path.join(workspace, "conf")
            speed = request.json['speed']
            cmdline = "python -u fuzz.py usbfuzzer --type fuzz --usb_fuzz_type bulk  --id {} --conf {} --workspace {} --interval {}".format(
                id,
                conf_path,
                workspace,
                speed)

    if sample_path != "":
        if type == "usb" and usb_fuzz_type == "ctrl":
            pass
        else:
            cmdline += " --sample {}".format(sample_path)

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


@app.route('/replay', methods=['POST'])
def replay():
    """
    创建一个重放任务
    :return:
    """
    if not request.json:
        return jsonify({"result": "fail", "msg": u"数据错误"})

    cmdline = ""
    type = request.json['type']
    crash_log = request.json['crash_log']
    crash_seq = crash_log['crash_seq']

    task_id = str(uuid.uuid1())
    workdir = os.path.dirname(__file__)
    workspace = os.path.join("/tmp/replay-{}".format(task_id))
    os.mkdir(workspace)

    # 存放 crash 序列的文件路径
    crash_path = os.path.join(workspace, "crash.json")
    # 存放正常交互序列的文件
    nomal_path = os.path.join(workspace, "normal.json")

    if (crash_log.has_key("usb_fuzz_type")):
        usb_fuzz_type = crash_log['usb_fuzz_type']
    else:
        normal_conf_data = crash_log['normal_configure']
        with open(nomal_path, "w") as fp:
            fp.write(json.dumps(normal_conf_data))

    with open(crash_path, "w") as fp:
        fp.write(json.dumps(crash_seq))

    if type == "tcp":
        t1 = request.json['t1']
        t2 = request.json['t2']
        speed = request.json['speed']
        cmdline = "python -u fuzz.py tcpfuzzer --type replay --host {} --port {} --interval {}  --workspace {} --conf {} --crash_path {}".format(
            t1, t2, speed, workspace, nomal_path, crash_path)

    elif type == "udp":
        t1 = request.json['t1']
        t2 = request.json['t2']
        speed = request.json['speed']
        cmdline = "python -u fuzz.py udpfuzzer --type replay --host {} --port {} --interval {}  --workspace {} --conf {} --crash_path {}".format(
            t1, t2, speed, workspace, nomal_path, crash_path)

    elif type == "serial":
        t1 = request.json['t1']
        t2 = request.json['t2']
        speed = request.json['speed']
        cmdline = "python -u fuzz.py serialfuzzer --type replay --device {} --baud {} --interval {}  --workspace {} --conf {} --crash_path {}".format(
            t1, t2, speed, workspace, nomal_path, crash_path)
    else:
        t1 = request.json['t1']
        t2 = request.json['t2']
        id = "{}:{}".format(t1, t2)

        usb_fuzz_type = request.json['usb_fuzz_type']

        if usb_fuzz_type == "ctrl":
            cmdline = "python -u fuzz.py usbfuzzer --type replay --id {}  --workspace {} --crash_path {}".format(id,
                                                                                                                 workspace,
                                                                                                                 crash_path)
        elif usb_fuzz_type == "bulk":
            speed = request.json['speed']
            cmdline = "python -u fuzz.py usbfuzzer --type replay --usb_fuzz_type bulk  --id {} --conf {} --workspace {} --interval {} --crash_path {}".format(
                id,
                nomal_path,
                workspace,
                speed, crash_path)

    cmd = Command(cmdline, workdir)
    THREADS[task_id] = cmd
    pid = cmd.run()
    ret = {
        "result": "successful",
        "task_id": task_id
    }

    return jsonify(ret)


@app.route('/replay-stop/<task_id>/', methods=['GET'])
def replay_stop(task_id):
    workspace = os.path.join("/tmp/replay-{}".format(task_id))

    cmd = "ps -ef | grep python | grep %s | awk  '{print $2}' |xargs  kill -9" % (workspace)
    os.system(cmd)
    ret = {
        "result": "successful"
    }
    return jsonify(ret)


@app.route('/replay-status/<task_id>/', methods=['GET'])
def replay_status(task_id):
    """
    创建一个重放任务
    :return:
    """

    workspace = os.path.join("/tmp/replay-{}".format(task_id))

    result_path = os.path.join(workspace, "result.json")
    ret = {
        "result": "failed"
    }
    if os.path.exists(result_path):
        with open(result_path, "r") as fp:
            data = json.loads(fp.read())

        ret = {
            "result": "successful",
            "data": data
        }
        return jsonify(ret)

    if not is_process_alive(task_id):
        ret = {
            "result": "dead"
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

    save_path = "{}".format(os.path.join(data_dir.encode("utf-8"), f.filename.split(".")[0]))
    unzip_file(tmp_path, save_path)

    ret = {
        "result": "successful",
        "output_dir": save_path
    }
    return jsonify(ret)


@app.route('/download/<task_id>/', methods=['GET'])
def download(task_id):
    i = g.db.execute("select * from project_information where task_id='{}'".format(task_id)).fetchone()
    workspace = i[6]
    zip_file_name = "/tmp/{}-workspace.zip".format(task_id)
    zip_dir(workspace, zip_file_name)
    # sleep(10)
    return send_from_directory(os.path.dirname(zip_file_name), os.path.basename(zip_file_name), as_attachment=True)


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


def is_empty(dir):
    if os.path.isdir(dir) and len(os.listdir(dir)) == 0:
        return True

    return False


def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS project_information( task_id TEXT PRIMARY KEY, project_name TEXT, pid TEXT, start_time TEXT, crash_sequence TEXT, cmdline TEXT, workspace TEXT,status TEXT)')
    cursor.close()
    conn.commit()


def zip_dir(dirname, zipfilename):
    """
    压缩目录
    :param dirname:
    :param zipfilename:
    :return:
    """
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        # print arcname
        zf.write(tar, arcname)
    zf.close()


def unzip_file(zip_file, out_dir):
    """
    解压 zip 文件到目录
    :param zip_file:  zip 文件路径
    :param out_dir:  解压后的内容存放的路径， 如果目录不存在会新建目录
    :return:
    """
    if not os.path.exists(out_dir):
        os.mkdir(out_dir, 0777)
    zf = zipfile.ZipFile(zip_file)
    for name in zf.namelist():
        name = name.replace('\\', '/')
        # 去掉zip压缩的根目录
        save_name = "/".join(name.split("/")[1:])

        if name.endswith('/'):
            os.mkdir(os.path.join(out_dir, save_name))
        else:
            save_name = os.path.join(out_dir, save_name)
            save_dir = os.path.dirname(save_name)
            if not os.path.exists(save_dir):
                os.mkdir(save_dir, 0777)
            with open(save_name, 'wb') as fp:
                fp.write(zf.read(name))


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
    pid = str(pid)
    try:
        res = subprocess.check_output("ps -fp {}".format(pid), shell=True)
        if pid in res:
            return True
        else:
            return False
    except:
        return False


def is_process_alive(taskid):
    res = subprocess.check_output("ps -ef | grep python | grep {}".format(taskid), shell=True)

    if res.count(taskid) > 1:
        return True
    return False


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
