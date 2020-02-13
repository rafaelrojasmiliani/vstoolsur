''' This module contains classes to interact with the universal robots's
29999 port.
This port is called Dashboard.
'''
import socket
import select


class cDashBoardInterface(object):
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream = None

    def connect(self, host='localhost'):
        try:
            self.soc.connect((host, 29999))
        except socket.error as e:
            return False
        readable, _, _ = select.select([self.soc], [], [], 1.0)
        if (len(readable) == 1):
            self.stream = self.soc.makefile(mode="w")
            return True
        else:
            return False

    def sendAndReceive(self, msg):
        _, writable, _ = select.select([], [self.soc], [], 1.0)
        if (len(writable) == 1):
            # msg+='\n'
            self.soc.sendall(msg)
        else:
            print("error, can't write in socket")
        readable, _, _ = select.select([self.soc], [], [], 1.0)
        if (len(readable) == 1):
            return self.soc.recv(1000)
        else:
            return None

    def load(self, filename):
        res = self.sendAndReceive('load ' + filename + '\n')
        if res[0] == 'F' or res[0] == 'E':
            return False
        return True

    def play(self):
        res = self.sendAndReceive('play\n')
        if res is None:
            return False
        if res[0] == 'F':
            return False
        return True

    def stop(self):
        res = self.sendAndReceive('stop\n')
        if res[0] == 'F':
            return False
        return True

    def running(self):
        res = self.sendAndReceive('running\n')
        if res[17] == 'F' or res[17] == 'f':
            return False
        return True

    def robotmode(self):
        res = self.sendAndReceive('robotmode\n')
        return res[11:-1]

    def pause(self):
        res = self.sendAndReceive('pause\n')
        if res[0] == 'P':
            return True
        return False

    def get_loaded_program(self):
        res = self.sendAndReceive('get loaded program\n')
        if res[0] == 'N':
            return False
        return res[16:-1]

    def disconnect(self):
        self.soc.close()


class cDashBoardState(object):
    def __init__(self):
        self.is_connected = 0
        self.runnig = 0
        self.robotMode = 0
        self.programLoaded = 0
        self.programState = 0
        self.polyscopeVersion = 0
        self.safetyMode = 0
        self.is_connected = self.update()
        self.hostname = socket.gethostname()

    def update(self):
        dashboard = cDashBoardInterface()
        res = dashboard.connect()

        if not res:
            return 0
        self.runnig = dashboard.running()

        self.robotMode = dashboard.sendAndReceive('robotmode\n')
        self.robotMode = self.robotMode.split(':', 1)[-1]

        self.programLoaded = dashboard.sendAndReceive('get loaded program\n')
        self.programLoaded = self.programLoaded.split(':', 1)[-1]

        self.programState = dashboard.sendAndReceive('programState\n')
        self.programState = self.programState.split(':', 1)[-1]

        self.polyscopeVersion = dashboard.sendAndReceive('PolyscopeVersion\n')

        self.safetyMode = dashboard.sendAndReceive('safetymode\n')
        self.safetyMode = self.safetyMode.split(':', 1)[-1]
        dashboard.disconnect()
        return 1
