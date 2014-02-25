#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                   Nao Challenge 2014 Main Program                       # #
# ########################################################################### #
# # File: naoWalks.py                                                       # #
# ########################################################################### #
# # Creation:   2014-02-04                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Authors:    Nicolas SENAUD                                              # #
# #             Pierre-Guillaume LEGUAY                                     # #
# #             Nicolas SAREMBAUD                                           # #
# #                                                                         # #
# ########################################################################### #

import sys
import time
import numpy as np                  # Numpy:  Maths library.
import cv2                          # OpenCV: Visual recognition library.
import vision_definitions           # Image definitions macros.

from threading import Thread        # Multithreading librairy.
from optparse import OptionParser   # Parser to keep connexion with Nao.

# Nao's libraries.
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule


# ####################### CLASS TO CONTOL NAO'S WALK ######################## #

class NaoWalks(ALModule, Thread):
    """docstring for NaoWalks"""
    def __init__(self, name):
        Thread.__init__(self)
        ALModule.__init__(self, name)

        # Create new object display a colored message on computer's terminal.
        self.logs = logs()

        # Create an ALMotion proxy.
        self.motion = ALProxy("ALMotion")
        self.logs.display("Subscribed to an ALMotion proxy", "Good")


    # Method called by the Thread.start() method.
    def run(self):
        global direction
        global alpha
        global directions

        self.motion.post.angleInterpolation(["HeadYaw"],
                                             alpha,
                                             1,
                                             False)

        direction = self.motion.getAngles("HeadYaw", True)

        try:
            if (direction.pop() != directions.pop()):
                directions.append(direction.pop())

                self.stop()

                self.logs.display("Nao is walking in direction (radian):",
                                  "Default",
                                  str(direction.pop()))
                self.motion.moveTo(0.2, 0, direction.pop())

        except IndexError:
            pass

        global AnalyseANewPict
        AnalyseANewPict = True


    # Method called to stop Nao.
    def stop(self):
        self.motion.killMove()


    # Method called to properly delete the thread.
    def delete(self):
        self.motion.killMove()

# ############################### END OF CLASS ############################## #