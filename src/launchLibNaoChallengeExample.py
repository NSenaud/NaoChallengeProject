#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: launchLibNaoChallengeExample.py                                   # #
# ########################################################################### #
# # Creation:   2014-03-10                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   # #
# #                                                                         # #
# ########################################################################### #

"""
    Simplest python script to lauch the NaoChallengeGeoloc module.
"""

from naoqi import ALProxy
import vision_definitions
import time


IP="NaoCRIC.local"
PORT=9559

def main():
    print 'START TESTING NaoChallengeGeoloc MODULE'

    try:
        print "Creating NaoChallengeGeoloc proxy to ", IP
        NCProxy = ALProxy("NaoChallengeGeoloc",IP,PORT)

    except Exception,e:
        print "Error when creating NaoChallengeGeoloc proxy:"
        print str(e)
        return(1)

    try:
        print "Creating ALMotion proxy to ", IP
        AMProxy = ALProxy("ALMotion",IP,PORT)

    except Exception,e:
        print "Error when creating ALMotion proxy:"
        print str(e)
        return(2)

    try:
        print "Registering to ALVideoDevice"
        NCProxy.registerToVideoDevice(vision_definitions.kVGA,
                                      vision_definitions.kBGRColorSpace)

        print "Walk from 270 to 220"
        NCProxy.walkFromDmtxToDmtx(270, 220)

        try:
            while True:
                print "Turn around"
                AMProxy.moveTo(0, 0, (180*3.14/180))

                print "Walk from 220 to 280"
                NCProxy.walkFromDmtxToDmtx(220, 280)

                print "Turn around"
                AMProxy.moveTo(0, 0, (180*3.14/180))

                print "Walk from 280 to 220"
                NCProxy.walkFromDmtxToDmtx(280, 220)

        except KeyboardInterrupt:
            NCProxy.unRegisterFromVideoDevice()

        print "unRegister from ALVideoDevice"
        NCProxy.unRegisterFromVideoDevice()

    except KeyboardInterrupt:
        NCProxy.unRegisterFromVideoDevice()

    except Exception,e:
        print "NaoChallengeGeoloc test Failed:"
        print str(e)
        return(3)

if __name__ == "__main__":
  exit (main()) 