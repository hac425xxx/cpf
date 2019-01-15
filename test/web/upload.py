#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save("test.txt")
        return redirect(url_for('upload'))
    else:
        return render_template("upload.html")


@app.route('/download/', methods=['GET'])
def download():
    if request.method == "GET":
        return send_from_directory('/tmp', "cpf.zip", as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9999, debug=True)
