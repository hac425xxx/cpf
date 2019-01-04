#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask, render_template, request, redirect, url_for
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
