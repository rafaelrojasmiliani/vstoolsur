from dashboardinterface import cDashBoardState, cDashBoardInterface

from flask import Flask, render_template, request

import time
import socket
import select

app = Flask(__name__)


# Index route
@app.route("/", methods=['POST', 'GET'])
def index():
    """
      Display main page.
    """
    d = cDashBoardState()
    if d.is_connected != 1:
        return render_template(
            'error.html', _error='can\'t connect to the Dashboard server')
    if request.method == 'POST':
        action = request.form.get('action')
        di = cDashBoardInterface()
        if not di.connect():
            return render_template(
                'error.html', _error='can\'t connect to the Dashboard server')
        if action == 'play':
            di.play()
        elif action == 'pause':
            di.pause()
        elif action == 'stop':
            di.stop()
        di.disconnect()
    return render_template('dashboard.html', _dashboard=d)


@app.route("/move", methods=['POST', 'GET'])
def move():
    if request.method == 'POST':
        srv = ("localhost", 30001)
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.connect(srv)
        except socket.error as e:
            return 'error'
        readable, _, _ = select.select([soc], [], [], 1.0)
        if len(readable) == 1:
            stream = soc.makefile(mode="w")

        vel = float(request.form.get('speed'))
        acc = float(request.form.get('acceleration'))
        decc = 9.0
        stream.write('def program():\n')
        com = request.form.get('motion')
        if com == '+x':
            stream.write('speedl([{:.4f},0,0,0,0,0],{:.4f})\n'.format(
                vel, acc))
        elif com == '-x':
            stream.write('speedl([{:.4f},0,0,0,0,0],{:.4f})\n'.format(
                -vel, acc))
        elif com == '+y':
            stream.write('speedl([0,{:.4f},0,0,0,0],{:.4f})\n'.format(
                vel, acc))
        elif com == '-y':
            stream.write('speedl([0,{:.4f},0,0,0,0],{:.4f})\n'.format(
                -vel, acc))
        elif com == '+z':
            stream.write('speedl([0,0,{:.4f},0,0,0],{:.4f})\n'.format(
                vel, acc))
        elif com == '-z':
            stream.write('speedl([0,0,{:.4f},0,0,0],{:.4f})\n'.format(
                vel, acc))
        stream.write('stopl({:.6f})\n'.format(decc))
        stream.write('end\n')
        stream.flush()
        soc.close()

    return render_template('move.html')


if __name__ == "__main__":
    # Starts the app listening to port 5000 with debug mode
    app.run(host="0.0.0.0", debug=True)
