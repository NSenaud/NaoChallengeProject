#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                   Nao Challenge 2014 Main Program                       # #
# ########################################################################### #
# # File: ihm.py                                                            # #
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
#import cv2                          # OpenCV: Visual recognition library.
#import vision_definitions           # Image definitions macros.

from optparse import OptionParser   # Parser to keep connexion with Nao.

import logs

# Nao's libraries.
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

# ###################### CLASS TO HAVE NAO'S SPEAKING ####################### #

class NaoSpeak(ALModule):
    """docstring for NaoSpeak"""
    def __init__(self, name, message):
    
        ALModule.__init__(self, name)

        self.message = message

        self.logs = logs.logs()
        self.tts = ALProxy("ALTextToSpeech")
        self.logs.display("Subscribed to an ALTextToSpeech proxy",
                          "Good")

        

    def say(self, message, volume=0.3, language='french'):
        self.tts.setLanguage(language)
        self.tts.setVolume(volume)
        self.tts.say(message)
        

# ############################### END OF CLASS ############################## #



# ####################### CLASS TO CONTROL NAO'S LED ######################## #

class NaoLeds(ALModule):
    """docstring for NaoLedsOn"""
    def __init__(self, name, state):
        ALModule.__init__(self, name)

        self.state = state

        self.leds = ALProxy("ALLeds")
        self.logs.display("Subscribed to an ALLeds proxy",
                          "Good")


        


# ############################### END OF CLASS ############################## #
