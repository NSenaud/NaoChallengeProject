#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                   Nao Challenge 2014 Main Program                       # #
# ########################################################################### #
# # File: NaoChallenge.py                                                   # #
# ########################################################################### #
# # Creation:   2014-01-20                                                  # #
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

from threading import Thread, Event # Multithreading librairy.
from optparse import OptionParser   # Parser to keep connexion with Nao.

# Nao Challenge's library.
from NaoChallenge import logs
from NaoChallenge import ihm
from NaoChallenge import camLow
from NaoChallenge import followTheLine

# Aldebaran library for Nao.
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule


# Constants:
IP = "NaoCRIC.local"                 # Nao's domain name.
port = 9559                          # Nao's standard port.
mainVolume = 0.3                     # Volume of Nao's voice.
definition = vision_definitions.kQVGA # Definition of cam's pictures & videos.

# Flags:
NaoShouldWalk = None                # Does Nao have a direction to follow?
AnalyseANewPict = True              # Lauch a new picture analysis?

# Threads declaration to avoid errors:
RefreshCamThread = None             # Thead which look after cam's picts.
getDirectionFromLineThread = None   # Trajectory computation thread.
NaoWalksThread = None               # Nao walk control thread.
followTheLine = None                # Main thread with main loop.

# Global objects:
myBroker = None                     # Broker to keep connexion with Nao.
memory = None                       # A memory object to recall events.

# Global variables:
imgNAO = None                       # Current image from the cam.
direction = 0                       # Direction (in radian) Nao should follow.
directions = []
directions.append(-10)
alpha = None                        # Angle (in radian) of Nao's head.



# ############################## MAIN FUNCTION ############################## #

def main():
    # Create parser to keep in touch with Nao.
    parser = OptionParser()
    parser.set_defaults(pip = IP, pport = port)
    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport

    global myBroker
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, pip, pport)

    log = logs.logs()

    # Starting... *************************************************************
    NaoSpeakThread = ihm.NaoSpeak("ihmSpeakModule", "Je me prépare")
    NaoSpeakThread.start()

    # Picture from Nao's cam.
    pict = None
    
    # Create a flag:
    getANewPict = Event()
    # Set the flag to False:
    getANewPict.clear()
    # Create the camRefresh thread:
    RefreshCamThread = camLow.RefreshCam("camLowRefreshModule",
                                         getANewPict,
                                         pict)
    RefreshCamThread.start()

    # Create a flag:
    analyseANewPict = Event()
    # Set the flag to False:
    analyseANewPict.clear()
    getDirectionFromLineThread = directionFromLine.getDirectionFromLineThread(
                                         "directionFromLineModule",
                                         analyseANewPict,
                                         pict)

    NaoSpeakThread = ihm.NaoSpeak("ihmSpeakModule", "Je suis prêt")
    NaoSpeakThread.start()
    NaoSpeakThread.join()
    NaoSpeak = None

    # Started! ****************************************************************

    while True:
        # Ask for a new pict from cam:
        getANewPict.set()
        # Waiting for the pict:
        while (pict is None):
            pass

        # Analyse the new pict.
        analyseANewPict.set()



    # global followTheLine
    # # Create new thread.
    # followTheLine = followTheLineModule("followTheLine")
    # # Start the new thread.
    # followTheLine.start()


    # followTheLine.join()

    # self.motion.post.angleInterpolation(["HeadYaw"],
    #                                      0,
    #                                      1,
    #                                      True)
    # self.posture.goToPosture("Crouch", 1.0)
    # self.logs.display("Nao go to posture Crouch")

    # self.motion.setStiffnesses("Body", 0.0)
    # self.logs.display("Motors shot down")

    NaoLedsOnThread = ihm.NaoLeds("ihmLedsOnModule", "on")
    NaoLedsOnThread.start()

    NaoSpeakThread = ihm.NaoSpeak("ihmSpeakModule",
                            "Je suis prêt à reprendre le travail quand tu veux")
    NaoSpeakThread.start()

    myBroker.shutdown()
    # Waiting for threads sync:
    NaoLedsOnThread.join()
    NaoLedsOnThread = None
    NaoSpeakThread.join()
    NaoSpeakThread = None

    log.display("Broker unsubscribed")
    log.display("NAO IS IDLE", "Good")
    sys.exit(0)


# ############################### END FUNCTION ############################## #



# ############################## PROGRAM ENTRY ############################## #

if __name__ == '__main__':
    main()

# ############################### END OF FILE ############################### #