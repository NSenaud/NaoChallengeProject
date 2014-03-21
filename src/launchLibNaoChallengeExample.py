
# -*- coding: utf-8 -*-
"""
    Simple python script to test the NaoChallengeGeoloc module
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
        print "Registering to ALVideoDevice"
        NCProxy.registerToVideoDevice(vision_definitions.kVGA,
                                      vision_definitions.kBGRColorSpace)

        print "Walk from 270 to 220"
        NCProxy.walkFromDmtxToDmtx(270, 220)

        print "unRegister from ALVideoDevice"
        NCProxy.unRegisterFromVideoDevice()


    except Exception,e:
        print "NaoChallengeGeoloc test Failed:"
        print str(e)
        return(1)

if __name__ == "__main__":
  exit (main()) 