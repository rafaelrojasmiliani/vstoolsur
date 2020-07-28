''' Test the direct kinematics of the Universal robots.'''
import os
import numpy as np
import unittest
from vsurt.urmsgs.urmsgs import cUrCartesianInfo, cUrJointData

from vsurt.urdk.urdk import cUrdk
import time


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

    def test_jacobian_computation_time(self):
        ''' Compare compute the time the robot's take to compute and invert the jacobian
        '''
        ip = '127.0.0.1'

        urmodel = cUrdk(_ip=ip)

        N = 500
        dt_jac = 0.0
        dt_jac_inv = 0.0
        dt_jac_svd = 0.0
        q = np.random.rand(6)
        for _ in range(N):
            t0 = time.time()
            jac = urmodel.jac(q)
            t1 = time.time()
            jac_inv = np.linalg.inv(jac)
            t2 = time.time()
            res = np.linalg.svd(jac)
            t3 = time.time()

            dt_jac = t1 - t0
            dt_jac_inv = t2 - t1
            dt_jac_svd = t3 - t2

        print('jacobian time computation', dt_jac/N)
        print('jacobian inversion time  ', dt_jac_inv/N)
        print('jacobian svd time        ', dt_jac_svd/N)

def main():
    unittest.main()


if __name__ == '__main__':
    main()
