''' This module contains classes to interact with the universal robots's
29999 port.
This port is called Dashboard.
'''
import socket
import select
import telnetlib


class cDashboad(object):
    def __init__(self, _host, _port=29999):
        self.tn_ = telnetlib.Telnet(_host, _port)
        self.tn_.read_eager()

    def command(self, _cmdstr):
        ''' send a comman to the dashboard.
            _cmdstr string'''
        cmd = _cmdstr.encode('utf-8') + b'\n'
        self.tn_.write(cmd)
        return self.tn_.read_eager()

    def load(self, _filenamestr):
        cmd = 'load ' + _filenamestr
        res = self.command(cmd)
        if res[0] == 'F' or res[0] == 'E':
            return False
        return True

    def play(self):
        res = self.command('play')
        if res is None:
            return False
        if res[0] == 'F':
            return False
        return True

    def stop(self):
        res = self.command('stop')
        if res[0] == 'F':
            return False
        return True

    def running(self):
        res = self.command('running')
        if res[17] == 'F' or res[17] == 'f':
            return False
        return True

    def robotmode(self):
        res = self.command('robotmode')
        return res[11:-1]

    def pause(self):
        res = self.command('pause')
        if res[0] == 'P':
            return True
        return False

    def get_loaded_program(self):
        res = self.command('get loaded program')
        if res[0] == 'N':
            return False
        return res[16:-1]

    def disconnect(self):
        self.tn_.close()


class cDashboadState(object):
    def __init__(self, _host, _port):
        self.is_connected_ = 0
        self.runnig_ = 0
        self.robotMode_ = 0
        self.robotModel_ = 0
        self.programLoaded_ = 0
        self.programState_ = 0
        self.polyscopeVersion_ = 0
        self.safetyMode_ = 0

        self.host_ = _host
        self.port_ = _port

    def update(self):
        dashboard = cDashboad(self.host_, self.port_)
        self.runnig_ = dashboard.running()

        self.robotMode_ = dashboard.command('robotmode\n')
        self.robotMode_ = self.robotMode_.split(':', 1)[-1]

        self.programLoaded_ = dashboard.command('get loaded program\n')
        self.programLoaded_ = self.programLoaded_.split(':', 1)[-1]

        self.programState_ = dashboard.command('programState\n')
        self.programState_ = self.programState_.split(':', 1)[-1]

        self.polyscopeVersion_ = dashboard.command('PolyscopeVersion\n')

        self.safetyMode_ = dashboard.command('safetymode\n')
        self.safetyMode_ = self.safetyMode_.split(':', 1)[-1]
        dashboard.disconnect()
