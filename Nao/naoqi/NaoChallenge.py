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
# # Authors:    Nicolas SAREMBAUD                                           # #
# #                                                                         # #
# ########################################################################### #

import sys
import time

from optparse import OptionParser   # Parser to keep connexion with Nao.

# Nao Challenge's library.
from NaoChallenge import NCMod
from NaoChallenge import logs

# Aldebaran library for Nao.
from naoqi import ALBroker


# Constants:
IP = "NaoCRIC.local"                 # Nao's domain name.
port = 9559                          # Nao's standard port.

# Global objects:
myBroker = None                     # Broker to keep connexion with Nao. 
memory = None                       # memories objects to recall events.
FrontTactil = None                  
MiddleTactil = None
RearTactil = None
IrReceiver = None
NaoChallenge = None
names = list()
times = list()
keys = list()
                   

# ############################## MAIN FUNCTION ############################## #

def main():
    # Create parser to keep in touch with Nao.
    parser = OptionParser()
    parser.set_defaults(pip = IP, pport = port)
    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport

    global myBroker
    global ModSelection 
    global NaoChallenge
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, pip, pport)
    try:
        NaoChallenge = NCMod.NCModule("NaoChallenge")
        log = logs.logs()
        #NaoChallenge.start_memento()
        while True:
            time.sleep(1)
            pass

    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        try:
            NaoChallenge.RedTracker.stopTracker()
        except Exception,e:
            print e
        try:
            NaoChallenge.motion.stopMove()
        except Exception,e:
            print e
        log.display("sits down")
        NaoChallenge.posture.goToPosture("Crouch", 1.0)
        NaoChallenge.motion.setStiffnesses("Body", 0.0)
        NaoChallenge.sonarProxy.subscribe("myApplication")
        NaoChallenge.sonarProxy.unsubscribe("myApplication")
        log.display("Broker unsubscribed")
        try:
            NaoChallenge.NCProxy.unRegisterFromVideoDevice() 
        except:
            time.sleep(0.1)
        time.sleep(2)
        
        myBroker.shutdown()
       
        log.display("Broker unsubscribed")
        log.display("NAO IS IDLE", "Good")
        sys.exit(0)


# ############################### END FUNCTION ############################## #



# ############################## PROGRAM ENTRY ############################## #

if __name__ == '__main__':
    main()

# ############################### END OF FILE ############################### #
