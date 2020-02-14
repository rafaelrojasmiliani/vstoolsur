'''
    This module contains several classes to handle UR messages from 30000-30001
    ports.
'''
import numpy as np
import socket
import struct
import copy

ROBOT_STATE = 16

JOINT_DATA = 1
ROBOT_MODE_DATA = 0
CARTESIAN_INFO = 4
CONFIGURATION_DATA = 6
KINEMATICS_INFO = 5


class cUrMessage(object):
    '''
        The output of the UR is composed by several messages.
        This class represent a binary message.
        self.data_ (binary) binary data associated with the message
        self.len_  (int) length of the message in bytes
        self.type_ (int) type of the message
    '''

    def __init__(self, _soc=None):
        """__init__

        :param _soc: socket connected to the UR
        """
        self.data_ = None
        self.len_ = None
        self.data_ = None
        self.type_ = None
        if _soc is not None:
            self.get(_soc)

    def get(self, _soc):
        """get the message from the socket _soc.

        :param _soc:
        """
        self.data_ = copy.copy(_soc.recv(4))
        self.len_ = struct.unpack('>i', self.data_)[0]
        self.data_ += copy.copy(_soc.recv(self.len_ - 4))
        self.type_ = struct.unpack('>b', self.data_[4:5])[0]

        return self


class cUrRobotStatePacket(object):
    """cUrRobotStatePacket
        Represents a UR robot state packate
    """

    def __init__(self, _data=None):
        self.len_ = None
        self.data_ = None
        self.type_ = None

        if _data is not None:
            self.get(_data)

    def get(self, _data):
        self.len_, self.type_ = struct.unpack('>ib', _data[:4 + 1])
        self.data_ = copy.copy(_data[:self.len_])


def getRobotStatePacketArray(_msg):

    result = []
    if _msg.type_ != 16:
        return result

    readData = 5
    while (readData < _msg.len_):
        pack = cUrRobotStatePacket(_msg.data_[readData:])
        result.append(pack)
        readData += pack.len_

    return result


class cUrCartesianInfo(object):
    def __init__(self, _data=None):
        self.tcpPose = None
        self.tcpOffset = None

        if _data is not None:
            self.unpack(_data)

    def unpack(self, _data):
        tcpPose = struct.unpack('>6d', _data[5:5 + 8 * 6])
        tcpOffset = struct.unpack('>6d', _data[5 + 8 * 6:5 + 8 * 6 + 8 * 6])
        self.tcpPose = np.array(tcpPose)
        self.tcpOffset = np.array(tcpOffset)

    def get(self, _ip, _port):
        pac = get_rs_packet(CARTESIAN_INFO, _ip, _port)
        self.unpack(pac.data_)


class cUrJointData(object):
    def __init__(self, _data=None):

        self.q_actual_ = None
        self.q_target_ = None
        self.qd_actual_ = None
        self.i_actual_ = None
        self.v_actual_ = None
        self.t_motor_ = None
        self.t_micro_ = None
        self.joint_mode_ = None
        fmtsz = 6*(
                   3 * (('>d', 8), ) +
                   (('>f', 4), ) +
                   (('>f', 4), ) +
                   (('>f', 4), ) +
                   (('>f', 4), ) +
                   (('>B', 1), ) )
        content_size = 0
        for (_, size) in fmtsz:
            content_size += size

        self.content_size_ = content_size

        self.fmtsz_ = fmtsz  # format and sizes

        if _data is not None:
            self.unpack(_data)

    def unpack(self, _data):
        rd = 5  # jump the size and the package type
        d = []
        for (fmt, sz) in self.fmtsz_:
            d.append(struct.unpack(fmt, _data[rd:rd + sz]))
            rd += sz

        self.q_actual_ = np.array(d[0])
        self.q_target_ = np.array(d[1])
        self.qd_actual_ = np.array(d[2])
        self.i_actual_ = np.array(d[3])
        self.v_actual_ = np.array(d[4])
        self.t_motor_ = np.array(d[5])
        self.t_micro_ = np.array(d[6])
        self.joint_mode_ = np.array(d[7])

    def get(self, _ip, _port):
        pac = get_rs_packet(JOINT_DATA, _ip, _port)
        assert pac.len_ - 4 == self.content_size_, '''
        Error: the paket downloaded from the robot does not have the correct size0'''
        self.unpack(pac.data_)


def get_rs_packet(_type, _ip, _port):
    '''
       get robot state packet:

        Parameters:
        ----------

    '''
    socket.setdefaulttimeout(None)
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((_ip, _port))
    msg = cUrMessage()
    while (1):
        msg.get(soc)
        rs_packets = getRobotStatePacketArray(msg)
        mypackets = [pac for pac in rs_packets if pac.type_ == _type]
        if len(mypackets) > 0:
            break
    soc.close()
    return mypackets[0]


class cUrConfigurationData(object):
    def __init__(self, _data=None):

        self.joinMinLimit_ = np.zeros((6, ))
        self.joinMaxLimit_ = np.zeros((6, ))

        self.joinMaxSpeed_ = np.zeros((6, ))
        self.joinMaxAcceleration_ = np.zeros((6, ))

        self.vJointDefault_ = 0.0
        self.aJointDefault_ = 0.0

        self.vToolDefatul_ = 0.0
        self.aToolDefatul_ = 0.0

        self.eqRadius_ = 0.0

        self.DHa_ = np.zeros((6, ))
        self.DHd_ = np.zeros((6, ))
        self.DHalpha_ = np.zeros((6, ))
        self.DHtheta_ = np.zeros((6, ))

        self.masterboardVersion = 0

        self.controllerBoxType = 0

        self.robotType = 0

        self.roboSubType = 0

    def unpack(self, _data):
        rd = 5  # read data

        self.joinMinLimit_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48
        self.joinMaxLimit_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48

        self.joinMaxSpeed_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48
        self.joinMaxAcceleration_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48

        self.vJointDefault_ = struct.unpack('>d', _data[rd:rd + 8])[0]
        rd += 8
        self.aJointDefault_ = struct.unpack('>d', _data[rd:rd + 8])[0]
        rd += 8
        self.vToolDefatul_ = struct.unpack('>d', _data[rd:rd + 8])[0]
        rd += 8
        self.aToolDefatul_ = struct.unpack('>d', _data[rd:rd + 8])[0]
        rd += 8
        self.eqRadius_ = struct.unpack('>d', _data[rd:rd + 8])[0]
        rd += 8

        self.DHa_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48
        self.DHd_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48
        self.DHalpha_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48
        self.DHtheta_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48

        self.masterboardVersion = struct.unpack('>i', _data[rd:rd + 4])[0]
        rd += 4

        self.controllerBoxType = struct.unpack('>i', _data[rd:rd + 4])[0]
        rd += 4

        self.robotType = struct.unpack('>i', _data[rd:rd + 4])[0]
        rd += 4

        self.roboSubType = struct.unpack('>i', _data[rd:rd + 4])[0]
        rd += 4

    def get(self, _ip, _port):
        pac = get_rs_packet(CONFIGURATION_DATA, _ip, _port)
        self.unpack(pac.data_)


class cUrKinematicsInfo(object):
    def __init__(self, _data=None):

        self.checksum_ = np.zeros((6, ), dtype=np.uint32)

        self.DHa_ = np.zeros((6, ))
        self.DHd_ = np.zeros((6, ))
        self.DHalpha_ = np.zeros((6, ))
        self.DHtheta_ = np.zeros((6, ))

        self.calibration_status_ = 0

    def unpack(self, _data):
        rd = 5  # size and packet type int+char

        self.checksum_[:] = struct.unpack('>6I', _data[rd:rd + 24])
        rd += 24

        self.DHtheta_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48
        self.DHa_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48
        self.DHd_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48
        self.DHalpha_[:] = struct.unpack('>6d', _data[rd:rd + 48])
        rd += 48

        self.calibration_status_ = struct.unpack('>I', _data[rd:rd + 4])[0]
        rd += 4

    def get(self, _ip, _port):
        pac = get_rs_packet(KINEMATICS_INFO, _ip, _port)
        self.unpack(pac.data_)


def test():
    import time

    confinfo = cUrKinematicsInfo()

    while (1):
        confinfo.get('10.10.238.32', 30001)
        print(repr(confinfo.DHa_))
        print(repr(confinfo.DHd_))
        print(repr(confinfo.DHalpha_))
        print(repr(confinfo.DHtheta_))
        print('-------------------------')
        time.sleep(0.05)


if __name__ == '__main__':
    test()
