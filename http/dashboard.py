from vsurt.dashboard import cDashboardState, cDashboard

from flask import Flask, render_template, request

import time

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

app.run(host="0.0.0.0", debug=True)
