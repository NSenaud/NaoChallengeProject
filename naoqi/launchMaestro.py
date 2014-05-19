#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: launchMaestro.py                                                  # #
# ########################################################################### #
# # Creation:   2014-05-07                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   # #
# #                                                                         # #
# ########################################################################### #

"""
    Launch Masetro trial of Nao Challenge 2014.
"""


import sys
import numpy as np                  # Numpy:  Maths library.
import cv2                          # OpenCV: Visual recognition library.
import vision_definitions           # Image definitions macros.

# Nao's Libraries.
from naoqi import ALProxy

# Calendar reading
from NaoChallenge import getCalendarDay 

fromDmtx = 270
toDmtx = 210 # Maestro


IP="NaoCRIC.local"
Port=9559


def main():
    print 'START TESTING NaoChallengeGeoloc MODULE'

    try:
        print "Creating NaoChallengeGeoloc proxy to ", IP
        NCProxy = ALProxy("NaoChallengeGeoloc",IP,Port)

    except Exception,e:
        print "Error when creating NaoChallengeGeoloc proxy:"
        print str(e)
        return(1)

    try:
        print "Creating ALMotion proxy to ", IP
        AMProxy = ALProxy("ALMotion",IP,Port)

    except Exception,e:
        print "Error when creating ALMotion proxy:"
        print str(e)
        return(2)

    try:
        print "Registering to ALVideoDevice"
        NCProxy.registerToVideoDevice(vision_definitions.kVGA,
                                      vision_definitions.kBGRColorSpace)

        NCProxy.walkFromDmtxToDmtx(int(fromDmtx), int(toDmtx))

    except KeyboardInterrupt:
        NCProxy.unRegisterFromVideoDevice()

    except Exception,e:
        print "NaoChallengeGeoloc test Failed:"
        print str(e)
        print "unRegister from ALVideoDevice"
        NCProxy.unRegisterFromVideoDevice()
        return(3)

    try:
        getCalendarDay.maestroReading()
    except Exception,e:
        print e

    print "unRegister from ALVideoDevice"
    NCProxy.unRegisterFromVideoDevice()

if __name__ == "__main__":
    exit (main())
