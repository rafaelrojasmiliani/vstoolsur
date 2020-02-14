'''
Universal robot direct kinematics
'''
import numpy as np

import itertools
from urmsgs import cUrCartesianInfo, cUrKinematicsInfo
from vsdk import cVsdk
import os


class cUrdk(cVsdk):
    def __init__(self, **args):
        super().__init__()
        if '_ururi' in args.keys():
            ururi = args['_ururi'] 
            res = os.system("ping -c 1 " + ururi)
            if res != 0:
                raise ValueError('The robot is not online')
        else:
            assert '_model' in args

        self.m6ee = np.eye(4)

        self.m6ee[:3, -1] = c.tcpOffset[:3]



