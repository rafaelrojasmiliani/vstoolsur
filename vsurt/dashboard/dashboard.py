''' This module contains classes to interact with the universal robots's
29999 port.
This port is called Dashboard.
'''
import socket
import select
import telnetlib


class cDashboard(object):
    def __init__(self, _host, _port=29999):
        self.tn_ = telnetlib.Telnet(_host, _port)
        self.tn_.read_until(b'\n')

    def command(self, _cmdstr):
        ''' send a comman to the dashboard.
            _cmdstr string'''
        cmd = _cmdstr.encode('utf-8') + b'\n'
        self.tn_.write(cmd)
        res = self.tn_.read_until(b'\n').decode('utf-8')[:-1]
        return res

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
        return res

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


class cDashboardState(object):
    def __init__(self, _host, _port=29999):
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
        dashboard = cDashboard(self.host_, self.port_)
        self.runnig_ = dashboard.running()

        self.robotMode_ = dashboard.command('robotmode')

        self.programLoaded_ = dashboard.command('get loaded program')

        self.programState_ = dashboard.command('programState')

        self.polyscopeVersion_ = dashboard.command('PolyscopeVersion')

        self.safetyMode_ = dashboard.command('safetymode')
        dashboard.disconnect()
