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
#import cv2                          # OpenCV: Visual recognition library.
import vision_definitions           # Image definitions macros.

from optparse import OptionParser   # Parser to keep connexion with Nao.

# Nao Challenge's library.
from NaoChallenge import logs
from NaoChallenge import ihm
from NaoChallenge import followTheLine

# Aldebaran library for Nao.
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
from optparse import OptionParser


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
memory = None                       # memories objects to recall events.
ModSelection = None
FrontTactil = None
MiddleTactil = None
RearTactil = None

# Global variables:
imgNAO = None                       # Current image from the cam.
direction = 0                       # Direction (in radian) Nao should follow.
directions = []
directions.append(-10)
alpha = None                        # Angle (in radian) of Nao's head.

# ################################# Class ################################### #

class ModSelectionModule(ALModule):
    """docstring for ModSelection"""
    def __init__(self,name):
        ALModule.__init__(self, name)

        # Create new object display a colored message on computer's terminal.
        self.logs = logs.logs()
        self.logs.display("tactil initialisation")
        
        # Create new proxies.
        self.tts = ALProxy("ALTextToSpeech", IP, port)
        self.logs.display("Subscribed to an ALTextToSpeech proxy",
                          "Good")
        self.motion = ALProxy("ALMotion", IP, port)
        self.logs.display("Subscribed to an ALMotion proxy",
                          "Good")
        self.posture = ALProxy("ALRobotPosture")
        self.logs.display("Subscribed to an ALRobotPosture proxy",
                          "Good")

        self.leds = ALProxy("ALLeds")
        self.logs.display("Subscribed to an ALLeds proxy",
                          "Good")

        # Prepare Nao.
        self.posture.goToPosture("StandInit", 1.0)
        self.logs.display("Nao is going to posture StandInit")
        self.motion.moveInit()
        self.logs.display("Initialisation of motion modules")


        # Ready!
        self.logs.display("Module ready", "Good")
        self.tts.post.say("Que dois-je faire maître")


        # select a Mod

        global FrontTactil
        global MiddleTactil
        global RearTactil      

        FrontTactil = ALProxy("ALMemory")
        MiddleTactil = ALProxy("ALMemory")
        RearTactil = ALProxy("ALMemory")

        FrontTactil.subscribeToEvent("FrontTactilTouched",
                                     "ModSelection",
                                     "start_memento")
        MiddleTactil.subscribeToEvent("MiddleTactilTouched",
                                      "ModSelection",
                                      "start_maestro")
        RearTactil.subscribeToEvent("RearTactilTouched",
                                    "ModSelection",
                                    "start_gato")

    def start_memento (self,*_args):

        FrontTactil.unsubscribeToEvent("FrontTactilTouched",
                                       "ModSelection")

        self.tts.post.say("je m'occupe de la clef")

        # Walk to the Door
        self.motion.moveTo(0.2, 0, 0) # Here will stand homemade C++ locomotion fonction (Vision.cpp) 
        self.logs.display("Going to the Door")

        # Get the Key
        

        # Walk where the Key is suppose to be
        self.motion.moveTo(0.2, 0, 3.1415) # Here will stand homemade C++ locomotion fonction (Vision.cpp) 
        

        # Drop the Key


        FrontTactil.subscribeToEvent("FrontTactilTouched",
                                     "ModSelection",
                                     "start_memento")

    

    def start_maestro (self,*_args):

        MiddleTactil.unsubscribeToEvent("MiddleTactilTouched",
                                        "ModSelection")

        self.tts.post.say("quel jour sommes nous aujourd'hui ?")

        # Walk to the Calendar
        self.motion.moveTo(0.2, 0, 1.57)
        self.logs.display("Go to the Calendar")

        # Read the Calendar


        # Act depending on the day


        MiddleTactil.subscribeToEvent("MiddleTactilTouched",
                                      "ModSelection",
                                      "start_maestro")
    
    

    def start_gato(self,*_args):

        RearTactil.unsubscribeToEvent("RearTactilTouched",
                                      "ModSelection")

        self.tts.post.say("c'est l'heure des croquette du chat !")

        # Walk to the Dropper
        self.motion.moveTo(0.2, 0, -1.57)
        self.logs.display("Go to the Dropper")

        # Turn it On

        RearTactil.subscribeToEvent("RearTactilTouched",
                                    "ModSelection",
                                    "start_gato")

    

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
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, pip, pport)
    
    ModSelection = ModSelectionModule("ModSelection")
    log = logs.logs()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        self.tts.post.NaoLeds("ihmLedsOnModule", "on")
        self.tts.post.say("Je suis prêt à reprendre le travail quand tu veux")

        myBroker.shutdown()
       
        log.display("Broker unsubscribed")
        log.display("NAO IS IDLE", "Good")
        sys.exit(0)


# ############################### END FUNCTION ############################## #



# ############################## PROGRAM ENTRY ############################## #

if __name__ == '__main__':
    main()

# ############################### END OF FILE ############################### #
