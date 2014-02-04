#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                   Nao Challenge 2014 Main Program                       # #
# ########################################################################### #
# # File: followTheLine.py                                                  # #
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

# ######################## MAIN CLASS AND MAIN LOOP ######################### #

class followTheLineModule(ALModule, Thread):
    """docstring for followTheLineModule"""
    def __init__(self, name):
        Thread.__init__(self)
        ALModule.__init__(self, name)

        # Create new object display a colored message on computer's terminal.
        self.logs = logs()
        self.logs.display("Initializing line following module...")
        
        # Create new proxies.
        self.posture = ALProxy("ALRobotPosture")
        self.logs.display("Subscribed to an ALRobotPosture proxy",
                          "Good")

        self.leds = ALProxy("ALLeds")
        self.logs.display("Subscribed to an ALLeds proxy",
                          "Good")

        # Prepare Nao.
        self.posture.goToPosture("StandInit", 1.0)
        self.logs.display("Nao is going to posture StandInit")

        # Create new threads.
        global getDirectionFromLineThread
        if (getDirectionFromLineThread is None):
            getDirectionFromLineThread = getDirectionFromLine("getDirectionFromLine")
            self.logs.display("New thread 'getDirectionFromLine' created",
                              "Good")

        global NaoWalksThread
        if (NaoWalksThread is None):
            NaoWalksThread = NaoWalks("NaoWalks")
            self.logs.display("New thread 'NaoWalks' created",
                              "Good")

        global RefreshCamThread
        if (RefreshCamThread is None):
            RefreshCamThread = RefreshCam("RefreshCam")
            self.logs.display("New thread 'RefreshCam' created",
                              "Good")

        # Start thread.
        if (RefreshCamThread is not None and RefreshCamThread.isAlive()):
            pass
        else:
            RefreshCamThread.start()
            self.logs.display("Thread 'RefreshCam' started",
                              "Good")

        # Ready!
        self.logs.display("Module ready", "Good")
        self.tts.say("Je suis prêt")


    # Shut down Nao by clicking on his front head button.
    def onTouched(self, *_args):
        global memory
        memory.unsubscribeToEvent("FrontTactilTouched",
                                  "followTheLine")

        # Properly close threads.
        global getDirectionFromLineThread
        getDirectionFromLineThread.delete()
        global NaoWalksThread
        NaoWalksThread.delete()
        global RefreshCamThread
        RefreshCamThread.delete()
        global followTheLine
        followTheLine.delete()


    # Method called by the Thread.start() method.
    def run(self):
        global memory       
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("FrontTactilTouched",
                                "followTheLine",
                                "onTouched")

        # Start a new threads.
        global getDirectionFromLineThread
        getDirectionFromLineThread.start()

        while True:
            if (getDirectionFromLine is not None 
                and getDirectionFromLineThread.isAlive()):
                pass
            else:
                # Start a new thread.
                getDirectionFromLineThread = getDirectionFromLine("getDirectionFromLine")
                getDirectionFromLineThread.start()

            global NaoWalksThread
            global NaoShouldWalk
            if (NaoShouldWalk is True):
                self.leds.randomEyes(0.5)
                self.leds.on("FaceLeds")
                if (NaoWalksThread.isAlive() is not True):
                    # Start a new thread.
                    NaoWalksThread = NaoWalks("NaoWalks")
                    NaoWalksThread.start()
                    NaoWalksThread.join()

            else:
                self.tts.say("Je recherche la ligne")
                self.logs.display("No line found", "Warning")

                NaoWalksThread.stop()
                # if (NaoWalksThread is None or NaoWalksThread.isAlive() is not True):
                #     NaoWalksThread.stop()

                # Rotate red eyes.
                self.leds.rotateEyes(0xff0000, 1, 1)

            time.sleep(1)

# ############################### END OF CLASS ############################## #