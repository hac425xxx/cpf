#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import sqlite3
from flask import Flask, jsonify, request
from flask import g
import uuid
import os
import time
import json
import datetime

DATABASE = '/tmp/database.db'
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
        info['runtime_log'] = i[6]
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
    info['runtime_log'] = i[6]
    # 计算出运行时间，单位为 秒
    info['runtime'] = str(get_delta(int(info['start_time'])))

    # 从 运行日志文件中加载数据
    if os.path.exists(info['runtime_log']):
        runtime_log = {}
        with open(info['runtime_log'], "r") as fp:
            runtime_log = json.loads(fp.read())

        data = {
            "fuzz_count": runtime_log['fuzz_count'],
            "fuzz_time": info['runtime'],
            "fuzz_result": runtime_log['is_run'],
            "crash_seqs": runtime_log['crash_sequence']
        }

        ret = {
            "result": "successful",
            "data": data
        }
    else:
        ret = {
            "result": "fail",
            "data": u"实时日志文件加载失败"
        }

    return jsonify(ret)


@app.route('/stop/<task_id>/', methods=['GET'])
def stop(task_id):
    i = g.db.execute("select * from project_information where task_id='{}'".format(task_id)).fetchone()
    pid = int(i[2])

    print "kill process: {}".format(pid)

    ret = {
        "result": "successful"
    }
    return jsonify(ret)


@app.route('/create', methods=['POST'])
def create():
    """
    创建一个任务， 返回 task id
    :return:
    """
    if not request.json:
        return jsonify({"result": "fail", "msg": u"数据错误"})

    print request.json

    ret = {
        "result": "successful",
        "task_id": ""
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
    上传的文件应该是压缩文件
    :return:
    """
    if request.method == 'POST':
        f = request.files['file']
        f.save("test.txt")


def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS project_information( task_id TEXT PRIMARY KEY, project_name TEXT, pid TEXT, start_time TEXT, crash_sequence TEXT, cmdline TEXT, runtime_log TEXT)')
    cursor.close()
    conn.commit()


def insert(task_id, project_name, pid, start_time, crash_sequence, cmdline, runtime_log):
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
    (task_id, project_name, pid, start_time, crash_sequence, cmdline, runtime_log) 
    VALUES 
    (:task_id, :project_name, :pid, :start_time, :crash_sequence, :cmdline, :runtime_log)'''
    g.db.execute(sql, {'task_id': task_id, 'project_name': project_name, 'pid': pid, "start_time": start_time,
                       "crash_sequence": crash_sequence, "cmdline": cmdline, "runtime_log": runtime_log})
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


if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", debug=True)
