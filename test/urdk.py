''' Test the direct kinematics of the Universal robots.'''
import os
import numpy as np
import sympy as sp
import quadpy
import unittest
from urmsgs.urmsgs import cUrCartesianInfo, cUrJointData

from vsdk.vsdk import cVsdk


def ping(_hostname):
    res = os.system('ping -c 1 ' + _hostname)
    return res == 0


class cMyTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(cMyTest, self).__init__(*args, **kwargs)

    def test_dk_wrt_robot(self):
        ''' Compare the output of dk with the robot's output
        '''
        jointState = cUrJointData()
        
        ip = '10.10.238.32'
        port = 30001
        for i in range(1000):
            jointState.get(ip, port)

            q = jointState.q_actual_

            qd = jointState.qd_actual_






    

def main():
    unittest.main()


if __name__ == '__main__':
    main()
