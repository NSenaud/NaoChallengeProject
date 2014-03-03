
# -*- coding: utf-8 -*-
"""
    Simple python script to test the NaoChallengeGeoloc module
"""

from naoqi import ALProxy


IP="NaoCRIC.local"
PORT=9559

def main():
    print 'START TESTING NaoChallengeGeoloc MODULE'

    try:
        NaoChallengeGeoloc_Proxy = ALProxy("NaoChallengeGeoloc",IP,PORT)
    except Exception,e:
        print "Error when creating NaoChallengeGeoloc proxy:"
        print str(e)
        return(1)

    try:
        NaoChallengeGeoloc_Proxy.sayText("Hello, World!")
    except Exception,e:
        print "NaoChallengeGeoloc test Failed:"
        print str(e)
        return(1)

if __name__ == "__main__":
  exit (main()) 