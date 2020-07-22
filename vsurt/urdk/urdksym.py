'''
Universal robot direct kinematics symbolic model
'''
import numpy as np

import sympy as sp

import itertools
from ..urmsgs.urmsgs import cUrCartesianInfo, cUrKinematicsInfo
from vsdk.vsdksym import cVsdkSym
import os
from .kinematicdata import cUR3, cUR5, cUR10


class cUrdkSym(cVsdkSym):
    def __init__(self, **args):
        cVsdkSym.__init__(self)
        if '_q' in args:
            q = args['_q']
        else:
            q = sp.symbols('q[0:6]', real=True)
        self.kinf_ = cUrKinematicsInfo()
        self.cinf_ = cUrCartesianInfo()
        if '_ip' in args.keys():
            ip_robot = args['_ip']
            res = os.system("ping -c 1 " + ip_robot)
            if res != 0:
                raise ValueError('The robot is not online')
            self.kinf_.get(ip_robot, 30001)
            self.cinf_.get(ip_robot, 30001)
            self.tcp_offset_ = self.cinf_.tcp_offset_
        else:
            model = args['_model']
            if '_tcp_offset' in args:
                self.tcp_offset_ = args['_tcp_offset']
            else:
                self.tcp_offset_ = np.zeros((3, ))
            if model == 'ur3':
                self.kinf_ = cUR3
            elif model == 'ur5':
                self.kinf_ = cUR5
            elif model == 'ur10':
                self.kinf_ = cUR10
            else:
                raise ValueError('unknow model')
        self.set_tcp_offset(*self.tcp_offset_[:3])
        for i in range(6):
            dha = self.kinf_.dh_a_[i]
            dhd = self.kinf_.dh_d_[i]
            dhalpha = self.kinf_.dh_alpha_[i]
            dhtheta = self.kinf_.dh_theta_[i]
            self.add_link(dha, dhd, dhalpha, dhtheta, q[i])


def ur_sym_jac(**args):
    dk = cUrdkSym(**args)
    res = dk.jac()
    return res


def ur_sym_dk(**args):
    dk = cUrdkSym(**args)
    res = dk()
    return res
