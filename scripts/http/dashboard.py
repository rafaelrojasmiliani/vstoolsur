from vsurt.dashboard import cDashboardState, cDashboard

from flask import Flask, render_template, request

import time

import os
import re


def list_ur_files(wd):
    files_in_dir = os.listdir(wd)
    os.chdir(wd)
    regex = re.compile(r'.*urp$')
    urfiles = [fname for fname in files_in_dir if regex.match(fname)]
    folders = [fname for fname in files_in_dir if os.path.isdir(fname)]

    namelist = (folders, urfiles)

    return namelist

app = Flask(__name__)


# Index route
@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        db = cDashboard('10.10.238.32')
        if action == 'play':
            db.play()
        elif action == 'pause':
            db.pause()
        elif action == 'stop':
            db.stop()
        db.disconnect()

    dbs = cDashboardState('10.10.238.32')
    dbs.update()
    res = render_template('dashboard.html', _dashboard=dbs)
    return res


@app.route("/load", methods=['POST', 'GET'])
def load():
    wd = '/'
    if request.method == 'POST':
        action = request.form.get('action')
        if action[:2] == 'cd':
            if action[3:] == '..':
                wd = os.path.dirname(wd)
            else:
                wd = wd + action[3:]
        elif action == 'load':
            print('LOAD!!')

    dirlist, filelist = list_ur_files(wd)
    return render_template(
        'load.html', _wd=wd, _dirlist=[], _filelist=filelist)



app.run(host="0.0.0.0", debug=True)
