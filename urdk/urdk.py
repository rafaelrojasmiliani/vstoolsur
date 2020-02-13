'''
Universal robot direct kinematics
'''
import numpy as np

import itertools
from urmsgs import cUrCartesianInfo, cUrKinematicsInfo
from vsdk import cVsdk


class cUrdk(cVsdk):
    def __init__(self, **args):
        super().__init__()
        if '_ip' in args.keys():
            c = cUrCartesianInfo()
            c.get('10.10.238.37', 30001)
        else:
            assert '_model' in args

        self.m6ee = np.eye(4)

        self.m6ee[:3, -1] = c.tcpOffset[:3]



