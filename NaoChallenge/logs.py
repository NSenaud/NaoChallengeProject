#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                   Nao Challenge 2014 Main Program                       # #
# ########################################################################### #
# # File: logs.py                                                           # #
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

# ######################### CLASS TO LOG EVENTS ############################# #

class logs(object):

    # mutex

    def __init__(self):
        # Colors definition with ASCII extended codes.
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.ERROR = '\033[91m'
        self.ENDC = '\033[0m'


    # Display a colored message on computer's terminal.
    def display(self, message, logType="Default", additionalMessage=" "):
        # mutex lock
        if ((logType == "Default") or (logType == 3)):
            print self.OKBLUE  + "[ INFO ]"    + self.ENDC,
            print message,
            print additionalMessage
        elif ((logType == "Good") or (logType == 2)):
            print self.OKGREEN + "[ INFO ]"    + self.ENDC,
            print message,
            print additionalMessage
        elif ((logType == "Warning") or (logType == 1)):
            print self.WARNING + "[ WARNING ]" + self.ENDC,
            print message,
            print additionalMessage
        elif ((logType == "Error") or (logType == 0)):
            print self.ERROR   + "[ ERROR ]"   + self.ENDC,
            print message,
            print additionalMessage
        # mutex unlock

# ############################### END OF CLASS ############################## #