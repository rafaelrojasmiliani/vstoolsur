from dashboard import cDashBoardState, cDashBoardInterface

from flask import Flask, render_template, request

import time

app = Flask(__name__)


# Index route
@app.route("/", methods=['POST', 'GET'])
def index():
    d = cDashBoardState()
    return render_template('dashboard.html', _dashboard=d)


@app.route("/rtde2ros/<int:_action>", methods=['POST'])
def playstop(_action):
    d = cDashBoardInterface()
    d.connect()
    if _action == 1:
        d.play()
    if _action == 0:
        d.stop()
    if _action == 2:
        d.pause()
    d.disconnect()
    time.sleep(0.05)
    d = cDashBoardState()
    return render_template('dashboard.html', _dashboard=d)


# Starts the app listening to port 5000 with debug mode
app.run(host="0.0.0.0", debug=True)
