''' Test the direct kinematics of the Universal robots.'''
import os
import numpy as np
import unittest
from vsurt.urmsgs.urmsgs import cUrCartesianInfo, cUrJointData

from vsurt.urdk.urdk import cUrdk


def ping(_hostname):
    res = os.system('ping -c 1 ' + _hostname)
    return res == 0


class cMyTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_dk_wrt_robot(self):
        ''' Compare the output of dk with the robot's output
        '''
        ip = '10.10.238.32'
        port = 30001
        res = os.system("ping -c 1 " + ip)
        if res != 0:
            print('Cannot compare with the robot')
            return
        js = cUrJointData()
        ci = cUrCartesianInfo()

        urmodel = cUrdk(_ip=ip)

        for i in range(1):
            js.get(ip, port)
            ci.get(ip, port)

            q = js.q_actual_

            m0e = urmodel(q)
            x_nominal = m0e[:3, -1]

            x_test = ci.tcp_pose_[:3]

            e = np.abs(x_nominal - x_test)

            einf = np.max(e)

            print('''
                     x nominal      = {}
                     x test         = {}
                     error inf norm = {}
                  '''.format(
                *[np.array2string(v) for v in [x_nominal, x_test, einf]]))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
