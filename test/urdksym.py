''' Test the direct kinematics of the Universal robots.'''
import os
import numpy as np
import sympy as sp
import quadpy
import unittest
from vsurt.urmsgs.urmsgs import cUrCartesianInfo, cUrJointData

from vsurt.urdk.urdksym import cUrdkSym
from vsurt.urdk.urdksym import ur_sym_dk, ur_sym_jac 


class cMyTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        urmodel = cUrdkSym(_ip=ip)

        dk = urmodel()
        q = urmodel.q_

        dk = sp.lambdify(sp.Matrix(q), dk, 'numpy')



        for i in range(1):
            js.get(ip, port)
            ci.get(ip, port)

            q = js.q_actual_

            m0e = dk(*q)
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

    def test_constructor(self):
        ''' Test if the constructor works '''

        dkur3 = cUrdkSym(_model='ur3')
        dkur5 = cUrdkSym(_model='ur5')
        dkur10 = cUrdkSym(_model='ur10')

        dkur3()
        dkur5()
        dkur10()

    def test_variables(self):
        x = sp.symbols('x_0:6', real=True)

        dk = ur_sym_dk(_q=x, _model='ur3')
        jac = ur_sym_jac(_q=x, _model='ur3')

        for i in range(3):
            for j in range(6):
                jac_test = dk.diff(x[j])[i, 3]
                jac_nom = jac[i, j]

                res = sp.simplify(jac_nom - jac_test)
                res = sp.lambdify(sp.Matrix(x), res, 'numpy')
                for k in range(20):
                    xnum = np.random.rand(6)
                    assert abs(res(*xnum)) < 1.0e-8

        



def main():
    unittest.main()


if __name__ == '__main__':
    main()
