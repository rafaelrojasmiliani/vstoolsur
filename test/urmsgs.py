''' Test the direct kinematics of the Universal robots.'''
import os
import numpy as np
import sympy as sp
import quadpy
import unittest
from urmsgs.urmsgs import cUrCartesianInfo, cUrJointData 
from urmsgs.urmsgs import cUrKinematicsInfo

from vsdk.vsdk import cVsdk

import functools
import traceback
import sys
import pdb


def debug_on(*exceptions):
    if not exceptions:
        exceptions = (Exception, )

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions:
                info = sys.exc_info()
                traceback.print_exception(*info)
                pdb.post_mortem(info[2])

        return wrapper

    return decorator


def ping(_hostname):
    res = os.system('ping -c 1 ' + _hostname)
    return res == 0


class cMyTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(cMyTest, self).__init__(*args, **kwargs)

    @debug_on()
    def testgetmessages(self):
        ''' Get messages from UR
        '''
        jointState = cUrJointData()
        
        ip = '10.10.238.32'
        port = 30001
        print('---- Get Joint state packages ----')
        jointState.get(ip, port)

        q = jointState.q_actual_
        qd = jointState.qd_actual_

        print('''
        Current joint position = {}
        Current joint velocity = {}
        '''.format(*[np.array2string(v) for v in [q, qd]]))

        print('---- Get Kinematic info packages ----')
        kinf = cUrKinematicsInfo()
        kinf.get(ip, port)
        aa = [kinf.dh_a_, kinf.dh_d_, kinf.dh_alpha_, kinf.dh_theta_]
        ss = ['a', 'd', 'alfa', 'theta']

        for a, s in zip(aa, ss):
            print('''
        DH {} parameter array = {}
        '''.format(s, np.array2string(a))
    
        print('---- Get Cartesian info packages ----')

        cinf = cUrCartesianInfo()
        cinf.get(ip, port)
        print('''
        Current TCP pose    = {}
        Current TCP offset  = {}
        '''.format(*[np.array2string(v) for v in [cinf.tcpPose_, cinf.tcp_pose_, cinf.tcp_offset_]]))

def main():
    unittest.main()


if __name__ == '__main__':
    main()

