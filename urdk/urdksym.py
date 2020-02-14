'''
Universal robot direct kinematics symbolic model
'''
import numpy as np

import itertools
from urmsgs import cUrCartesianInfo, cUrKinematicsInfo
from vsdk.vsdksym import cVsdkSym
import os


class cUrdkSym(cVsdkSym):
    def __init__(self, **args):
        super().__init__()
        if '_ururi' in args.keys():
            ururi = args['_ururi'] 
            res = os.system("ping -c 1 " + ururi)
            if res != 0:
                raise ValueError('The robot is not online')
        else:
            assert '_model' in args, '''
            Error: you must specify a robot model!
            '''
            assert '_tcpoffset' in args


        self.setTCP(*c.tcpOffset[:3])




