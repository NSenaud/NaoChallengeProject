
# -*- coding: utf-8 -*-
"""
    Simple python script to test the NaoChallengeGeoloc module
"""

from naoqi import ALProxy
import vision_definitions
import random


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
        rand = random.randrange(8)

        if (rand == 1):
            NCProxy.sayText("Bobidi Bobida Taratata")
        elif (rand == 2):
            NCProxy.sayText("Nao a volé mon âme ! Au secours !")
        elif (rand == 3):
            NCProxy.sayText("Prout")
        elif (rand == 4):
            NCProxy.sayText("J'aime les moules")
        elif (rand == 5):
            NCProxy.sayText("Il est tard, je veux dormir, rentrez chez vous bandes de connards!")
        elif (rand == 6):
            NCProxy.sayText("Je mangerais bien un Bovitch à la crème")
        elif (rand == 7):
            NCProxy.sayText("Bzzz Wip Croutche")
        else:
            NCProxy.sayText("J'aime les teletobiz")

        print "Registering to ALVideoDevice"
        NCProxy.registerToVideoDevice(vision_definitions.kVGA,
                                      vision_definitions.kBGRColorSpace)

        print "NCProxy.findLine()"
        NCProxy.findLine()

        print "unRegister from ALVideoDevice"
        NCProxy.unRegisterFromVideoDevice()

    except Exception,e:
        print "NaoChallengeGeoloc test Failed:"
        print str(e)
        return(1)

if __name__ == "__main__":
  exit (main()) 