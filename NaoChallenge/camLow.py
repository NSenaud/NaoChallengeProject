#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                   Nao Challenge 2014 Main Program                       # #
# ########################################################################### #
# # File: camLow.py                                                         # #
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

from NaoChallenge import followTheLine

# Nao's libraries.
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

# ########################## CLASS TO REFRESH CAM ########################### #

class RefreshCam(ALModule, Thread):
    """docstring for NaoWalks"""
    def __init__(self, name):
        Thread.__init__(self)
        ALModule.__init__(self, name)

        # Create new object to get logs on computer's terminal.
        self.logs = logs()

        # Create an ALVideoDevice proxy.
        self.camProxy = ALProxy("ALVideoDevice")
        self.logs.display("Subscribed to an ALVideoDevice proxy", "Good")

        # Register a video module.
        colorSpace = vision_definitions.kBGRColorSpace
        fps = 1
        camera = 1      # 1 = mouth camera / 0 = front camera.
        self.followTheLineCam = self.camProxy.subscribeCamera("LowCam",
                                                              camera,
                                                              definition,
                                                              colorSpace,
                                                              fps)
        self.logs.display("Subscribed to Camera 1", "Good")


    # Method called by the Thread.start() method.
    def run(self):
        while True:
            # mouais ;)
            global AnalyseANewPict
            if (AnalyseANewPict is True):
                global imgNAO
                # Get the image.
                imgNAO = self.camProxy.getImageRemote(self.followTheLineCam)
                self.camProxy.releaseImage(self.followTheLineCam)
                self.logs.display("Received a picture from Camera 1")
            # AMA pultot 0.1, le but c'est juste de lui eviter une boucle infinie si AnalyseANewPict=False
            # Tu peux tester sans le sleep avec un self.logs.display("Je fais rien!! Je tourne en rond dans RefreshCam.run()")
            # pour voir si ca lui arrive souvent ou pas.
            # (sachant que le sleep n'est pas la meilleure facon de résoudre ce pb)
            time.sleep(0.1)


    # Method called to properly delete the thread.
    def delete(self):
        self.camProxy.unsubscribe("LowCam")
        self.logs.display("Camera unsubscribed", "Good")

# ############################### END OF CLASS ############################## #