'''
This module only contains the Official Kinematic data of the UR models
'''
import numpy as np


class cUR3(object):
    dh_a_ = (0.0, -0.24365, -0.21325, 0.0, 0.0, 0.0)
    dh_d_ = (0.1519, 0.0, 0.0, 0.11235, 0.08535, 0.0819)
    dh_alpha_ = (np.pi / 2.0, 0.0, 0.0, np.pi / 2.0, -np.pi / 2.0, 0.0)
    dh_theta_ = 6*(0.0, )


class cUR5(object):
    dh_a_ = (0.0, -0.425, -0.39225, 0.0, 0.0, 0.0)
    dh_d_ = (0.089159, 0.0, 0.0, 0.10915, 0.09465, 0.0823)
    dh_alpha_ = (np.pi / 2.0, 0.0, 0.0, np.pi / 2.0, -np.pi / 2.0, 0.0)
    dh_theta_ = 6*(0.0, )

class cUR10(object):
    dh_a_ = (0.0, -0.612, -0.5723, 0.0, 0.0, 0.0)
    dh_d_ = (0.1273, 0.0, 0.0, 0.163941, 0.1157, 0.0922)
    dh_alpha_ = (np.pi / 2.0, 0.0, 0.0, np.pi / 2.0, -np.pi / 2.0, 0.0)
    dh_theta_ = 6*(0.0, )
