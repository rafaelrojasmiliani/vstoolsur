'''
Universal robot direct kinematics
'''
import numpy as np

import itertools
from urmsgs.urmsgs import cUrCartesianInfo, cUrKinematicsInfo
from vsdk.vsdk import cVsdk
import os


class cUrdk(cVsdk):
    def __init__(self, **args):
        super().__init__()
        self.kinf_ = cUrKinematicsInfo()
        self.cinf_ = cUrCartesianInfo()
        if '_ip' in args.keys():
            ip_robot = args['_ip'] 
            res = os.system("ping -c 1 " + ip_robot)
            if res != 0:
                raise ValueError('The robot is not online')
            self.kinf_.get(ip_robot, 30001)
            self.cinf_.get(ip_robot, 30001)
            self.set_tcp_offset(*self.cinf_.tcp_offset_[:3])
            for i in range(6):
                dha = self.kinf_.dh_a_[i]
                dhd = self.kinf_.dh_d_[i]
                dhalpha = self.kinf_.dh_alpha_[i]
                dhtheta = self.kinf_.dh_theta_[i]
                self.add_link(dha, dhd, dhalpha, dhtheta)
        else:
            assert '_model' in args, ''' 
            Error: you must speficy which model are you using
            '''

