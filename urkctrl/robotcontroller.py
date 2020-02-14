''' Very simple module to implement a kinematic control of the UR robot.
'''
import urmsgs.rtde.rtde as rtde
import urmsgs.rtde.rtde_config as rtde_config
import numpy as np

from threading import Lock

from copy import deepcopy, copy

import time


class cRobotController(object):
    """
      This class is intended to be robot controller capable of sending commands
      directly to the RTDE server.
    """

    def __init__(self):
        """
          Initialize this class, initializating common variables
        """
        config_filename = 'rtdeinterface_conf.xml'  # RTDE configuration file
        conf = rtde_config.ConfigFile(config_filename)  # load conf file
        self.state_names, self.state_types = conf.get_recipe('state')
        self.iregHandler_names, self.iregHandler_types = conf.get_recipe(
            'setvelocity')
        #       self.watchdog_names, self.watchdog_types = conf.get_recipe('watchdog')

        self.keep_running = True

    def connect(self, host='10.10.238.32', port=30004):
        """
          This function connects to the correct robot.
            - If we are controlling the real robot, it
              connects to the RTDE server
        """
        # -------------------------------------------------
        # ------------- Connect to the robot RTDE server
        # -------------------------------------------------
        self.con = rtde.RTDE(host, port)
        handshake_result = self.con.connect()
        if not handshake_result:
            return False
        self.ver = self.con.get_controller_version()
        try:
            self.con.send_output_setup(self.state_names, self.state_types)
            self.iregHandler = self.con.send_input_setup(
                self.iregHandler_names, self.iregHandler_types)
        except ValueError:
            return False

        if not self.con.send_start():
            return False

        self.setInputZero()

        return True

    def setInputZero(self):
        self.iregHandler.input_double_register_0 = 0.0
        self.iregHandler.input_double_register_1 = 0.0
        self.iregHandler.input_double_register_2 = 0.0
        self.iregHandler.input_double_register_3 = 0.0
        self.iregHandler.input_double_register_4 = 0.0
        self.iregHandler.input_double_register_5 = 0.0
        self.iregHandler.input_double_register_6 = 0.0
        self.iregHandler.input_int_register_0 = 0
        self.iregHandler.input_int_register_1 = 0
        self.con.send(self.iregHandler)


    def getFeedback(self, *options):
        """
          Get the feedback from the robot

          Parameters:
          ----------
            *options: array of strings
              The accepted values are:
                - actual_q:  actual joint position
                - actual_qd: actual joint speeds

          Returns:
          -------
            res: tuple
              a tuple of arrays containts the requested information
        """
        res = ()
        self.state = self.con.receive()
        for key in options:
            res = res + (np.array(getattr(self.state, key)), )
        self.timeSeconds = time.time()
        return res

    def sendControl(self, target_qd, acc):
        """
          Send a velocity command to the robot.
        """
        self.iregHandler.input_double_register_0 = target_qd[0]
        self.iregHandler.input_double_register_1 = target_qd[1]
        self.iregHandler.input_double_register_2 = target_qd[2]
        self.iregHandler.input_double_register_3 = target_qd[3]
        self.iregHandler.input_double_register_4 = target_qd[4]
        self.iregHandler.input_double_register_5 = target_qd[5]
        self.iregHandler.input_double_register_6 = acc
        self.iregHandler.input_int_register_0 = 1
        self.iregHandler.input_int_register_1 = 1
        self.con.send(self.iregHandler)

    def disconnect(self, signal=None, frame=None):
        """
          Disconet. This only serves if we are contronlling the real robot.
        """
        self.con.send_pause()
        self.con.disconnect()

    def sleep(self, t):
        t0 = self.timeSeconds
        while (self.keep_running):
            self.getFeedback()
            t1 = self.timeSeconds
            if (t1 - t0 > t):
                break
