#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: readDataMatrix.py                                                 # #
# ########################################################################### #
# # Creation:   2014-04-07                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   # #
# #                                                                         # #
# ########################################################################### #

"""
    Read Datamatrix with ALDataMatrixDetection and create event with ALMemory.
"""

import sys
from naoqi import ALProxy
# from naoqi import ALMemory
import time


IP="NaoCRIC.local"
Port=9559


def main():
    print 'START readDataMatrix MODULE'

    # *** Proxies Creation ***
    try:
        # Datamatrix Detection Proxy creation:
        print "Creating ALDataMatrixDetection proxy to ", IP
        DDProxy = ALProxy("ALDataMatrixDetection", IP, Port)

    except Exception,e:
        print "Error when creating ALDataMatrixDetection proxy:"
        print str(e)
        return(2)

    try:
        # Datamatrix Notification Proxy creation:
        print "Creating ALMemory proxy to ", IP
        DNProxy = ALProxy("ALMemory", IP, Port)

    except Exception,e:
        print "Error when creating ALMemory proxy:"
        print str(e)
        return(3)

    try:
        # Text To Speech Proxy creation:
        print "Creating ALLeds proxy to ", IP       
        ALedsProxy = ALProxy("ALLeds", IP, Port)
    except Exception,e:
        print "Error when creating ALLeds proxy:"
        print str(e)
        return(4)


    print "Set resolution to VGA"
    DDProxy.setResolution(2)

    # Initialise Datamatrix Detection Event:
    DNProxy.declareEvent("DatamatrixDetection")

    
    try:
        while True:
            print "\nALDataMatrixDetection proxy Shooting..."
            DataMatrixDetected = DDProxy.processOneShot(False, [0,0])        
                
            try:
                DataMatrixValue = str(DataMatrixDetected[7][0][0])[2:5]
            
            except Exception,e:
                DataMatrixValue = 0
            
            if (int(DataMatrixValue) > 40 and int(DataMatrixValue) < 600):
                print "Datamatrix value:",
                print DataMatrixValue

                # Create Datamatrix Detection Event:
                DNProxy.raiseEvent("DatamatrixDetection", DataMatrixValue)

                ALedsProxy.off('FaceLeds')
                time.sleep(0.5)
                ALedsProxy.on('FaceLeds')

            time.sleep(1)

    except KeyboardInterrupt:
        DDProxy.unsubscribeCamera()

    except Exception,e:
        DDProxy.unsubscribeCamera()
        print "ALDataMatrixDetection test Failed:"
        print str(e)
        return(1)

if __name__ == "__main__":
    exit (main()) 