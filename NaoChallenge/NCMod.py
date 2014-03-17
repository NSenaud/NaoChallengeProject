#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #            Nao Challenge 2014, a library for the challenge              # #
# ########################################################################### #
# # File: NCMod.py                                                          # #
# ########################################################################### #
# # Creation:   2014-03-14                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Authors:    Nicolas SENAUD                                              # #
# #             Pierre-Guillaume LEGUAY                                     # #
# #             Nicolas SAREMBAUD                                           # #
# #                                                                         # #
# ########################################################################### #
# # Contain : NCModule                                                      # #
# #             - start_memento                                             # #
# #             - start_maestro                                             # #
# #             - start_gato                                                # #
# #             - GetObject                                                 # #
# #             - Eventsnit                                                 # #
# #             - TactilStart                                               # #
# #             - TactilStop                                                # #
# #             - IR_receiver                                               # #
# #                                                                         # #
# ########################################################################### #

import sys
import time
import numpy as np                  # Numpy:  Maths library.
import cv2                          # OpenCV: Visual recognition library.
import vision_definitions           # Image definitions macros.

# Parser to keep connexion with Nao.
from optparse import OptionParser

# Nao Challenge's library.
import logs
import ihm
import followTheLine
import timelines

# Aldebaran library for Nao.
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

# Constants:
IP = "NaoCRIC.local"                 # Nao's domain name.
ip = "NaoCRIC.local"
port = 9559                          # Nao's standard port.
PORT = 9559
mainVolume = 0.3                     # Volume of Nao's voice.
definition = vision_definitions.kVGA # Definition of cam's pictures & videos.
colors = vision_definitions.kBGRColorSpace


# Global objects:
myBroker = None                     # Broker to keep connexion with Nao.
memory = None                       # memories objects to recall events.
FrontTactil = None                  
MiddleTactil = None
RearTactil = None
IrReceiver = None

# ################################# Class ################################### #

class NCModule(ALModule):
    """docstring for Nao Challenge Module"""
    def __init__(self,name):
        self.name = name
        ALModule.__init__(self, name)
        # Create new object display a colored message on computer's terminal.
        self.logs = logs.logs()
        
        # Create new proxies.
        self.tts = ALProxy("ALTextToSpeech", IP, port)
        self.logs.display("Subscribed to an ALTextToSpeech proxy",
                          "Good")
        
        self.motion = ALProxy("ALMotion", IP, port)
        self.motion.moveInit()
        self.logs.display("Subscribed to an ALMotion proxy",
                          "Good")
        
        self.posture = ALProxy("ALRobotPosture")
        self.logs.display("Subscribed to an ALRobotPosture proxy",
                          "Good")

        self.leds = ALProxy("ALLeds")
        self.logs.display("Subscribed to an ALLeds proxy",
                          "Good")

        self.RedTracker = ALProxy("ALRedBallTracker",IP, port)
        self.logs.display("Subscribed to an ALRedBallTracker proxy",
                          "Good")

        self.Remote = ALProxy("ALInfrared", IP, port)
        self.Remote.initReception(10)
        self.logs.display("Subscribed to an ALInfrared proxy",
                          "Good")

        self.NCProxy = ALProxy("NaoChallengeGeoloc",IP,port)
        self.NCProxy.registerToVideoDevice(definition, colors)
        self.logs.display("Subscribed to an NaoChallengeGeoloc proxy",
                          "Good")
        
        self.NCMotion = timelines.TimelinesModule()
        self.logs.display("Timelines initialisation",
                          "Good")

        self.sonarProxy = ALProxy("ALSonar", ip, 9559)
        self.logs.display("Subscribed to an ALSonar proxy",
                          "Good")

        self.memoryProxy = ALProxy("ALMemory", ip, 9559)
        self.logs.display("Subscribed to an ALMemory proxy",
                          "Good")

        # Prepare Nao.
        self.posture.goToPosture("StandInit", 1.0)
        self.logs.display("Nao is going to posture StandInit")

        seld.EventsInit()
        self.logs.display("tactil initialisation")

        # Ready!
        self.logs.display("Module ready", "Good")

##############################################################################
##                            start_memento()                               ##
##                    A method to launch memento mod                        ##    
##                                                                          ##

    def start_memento (self,*_args):

        self.TactilStop()

        self.tts.post.say("je m'occupe de la clef")

        # Walk to the Door
        self.logs.display("Going to the Door")
        #self.NCProxy.post.followLine()
        #time.sleep(20)
        self.motion.moveTo(0.5, 0, 0)
        self.logs.display("Door Reach")

        # Get the Key
        while self.GetObject("Key","RedDetection") != True :
            time.sleep(3)

        # Walk where the Key is suppose to be
        self.logs.display("Going to the Key Case") 
        self.motion.moveTo(0, 0, 3.14)
 
        #self.post.NCProxy.followLine()
        self.logs.display("Key Case Reach")
        

        # Drop the Key
        while self.GetObject("KeyCase","RedDetection") != True :
            time.sleep(3)


        self.TactilStart()

    

##############################################################################
##                            start_maestro()                               ##
##                    A method to launch maestro mod                        ##    
##                                                                          ##
    def start_maestro (self,*_args):

        self.TactilStop()

        self.tts.post.say("quel jour sommes nous aujourd'hui ?")

        # Walk to the Calendar
        self.logs.display("Go to the Calendar")
        self.motion.moveTo(0.5, 0, 0)
        self.logs.display("Calendar Reach")

        # Read the Calendar


        # Act depending on the day


        self.TactilStart()
  

##############################################################################
##                            start_gato()                                  ##
##                    A method to launch gato mod                           ##    
##                                                                          ##

    def start_gato(self,*_args):

        self.TactilStop()

        self.tts.post.say("c'est l'heure des croquette du chat !")

        # Walk to the Dropper
        self.logs.display("Go to the Dropper")
        self.motion.moveTo(0.5, 0, 0)
        self.logs.display("Dropper Reach")

        # Turn it On
        self.NecRemote.sendRemoteKey("Sony_RM-ED009-12", "power")
        self.logs.display("IR message send")
        NecReceiver.subscribeToEvent("InfraRedRemoteKeyReceived",
                                     self.name,
                                     "IR_receiver")
        
        self.TactilStart()


##############################################################################
##                  GetObject("objective", "way")                        ##
##      A method to get the Nao closer to an object and act with it         ##    
##                                                                          ##
##      Return a boolean (True) when the objective is over                  ##
##                                                                          ##
##      The first given argument selects the objective and must be          ##
##      one of these srtings :                                              ##
##                  - "Key" (default)                                       ##
##                  - "KeyCase"                                             ##
##                  - "Dropper"                                             ##
##                                                                          ##
##      The second given argument selects the way to get closer to the key  ##                                                    
##      and must be one of these strings :                                  ##
##                  - "RedDetection" (default)                              ##
##                  - "Datamatrix"                                          ##
##                                                                          ##
    def GetObject(self, objective = "Key", way = "RedDetection"):

##        
        if way == "RedDetection":
            # locate the red ball on the screen
            self.key.startTracker()
            time.sleep(1)
            self.pos = self.key.getPosition()
            self.z = self.pos.pop()
            self.y = self.pos.pop()
            self.x = self.pos.pop()
            # getPosition() return [x,y,z] when there is a red "ball"
            if self.x + self.y + self.z != 0.0:
                # Get sonar left distance in meters 
                self.sonarProxy.subscribe("myApplication")
                self.LeftSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
                time.sleep(0.2)
                # Same thing for right.
                self.RightSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
                self.distance = (self.LeftSonar + self.RightSonar)/2.0
                time.sleep(0.2)
#
                # Go to the red object
                if objective == "Key":                    
                    while self.distance > 0.29:                
                        # Get sonars echos
                        self.LeftSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
                        self.RightSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
                        self.distance = (self.LeftSonar + self.RightSonar)/2.0
                        
                        self.head = self.motion.getAngles("Head",True)
                        self.head.reverse()
                        self.headyaw = self.head.pop()
                        self.motion.moveToward(0.7, 0, self.headyaw/2.0)

                        if self.key.isNewData():
                            self.logs.display("Distance from the key in cm")
                            self.logs.display(100*self.distance)
                    self.motion.stopMove()
                    self.motion.moveTo(0.08, 0, 0) 
                    self.logs.display(self.headyaw)
                    self.motion.moveTo(0, self.headyaw/3.7, 0)          
                    
                    self.NCMotion.GetTheKey()   # this line use a method in timelines.py which provide tables used after
                    self.motion.angleInterpolation(names, keys, times, True);

                    return True
#                   
                elif objective == "KeyCase":
                    while self.distance > 0.29:                
                        # Get sonars echos
                        self.LeftSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
                        self.RightSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
                        self.distance = (self.LeftSonar + self.RightSonar)/2.0
                        
                        self.head = self.motion.getAngles("Head",True)
                        self.head.reverse()
                        self.headyaw = self.head.pop()
                        self.motion.moveToward(0.7, 0, self.headyaw/2.0)
                        
                        if self.key.isNewData():
                            self.logs.display("Distance from the key in cm")
                            self.logs.display(100*self.distance)
                    self.motion.stopMove()
                    self.motion.moveTo(0.05, 0, 0)           
                   
                    self.NCMotion.DropTheKey()   # this line use a method in timelines.py which provide tables used after
                    self.motion.angleInterpolation(names, keys, times, True);

                    return True                   
#
                elif objective == "Dropper":
                    while self.distance > 0.29:                
                        # Get sonars echos
                        self.LeftSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
                        self.RightSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
                        self.distance = (self.LeftSonar + self.RightSonar)/2.0
                        
                        self.head = self.motion.getAngles("Head",True)
                        self.head.reverse()
                        self.headyaw = self.head.pop()
                        self.motion.moveToward(0.7, 0, self.headyaw/2.0)
                        
                        if self.key.isNewData():
                            self.motion.moveToward(0.7, 0, self.headyaw/2.0)
                            self.logs.display("Distance from the key in cm")
                            self.logs.display(100*self.distance)
                    self.motion.stopMove()
                    self.motion.moveTo(0.05, 0, 0)           
                    
                    self.NCMotion.PressTheButton()   # this line use a method in timelines.py which provide tables used after
                    self.motion.angleInterpolation(names, keys, times, True);

                    return True                   

            # getPosition methode return [0,0,0] when there is no red ball
            elif self.x + self.y + self.z == 0.0:
            # So we're here if there is no visible key
                self.logs.display("The red object isn't visible")
                return False

            # random error 
            else:
                self.logs.display("The position of the red object wasn't in the right type")
                self.logs.display("So it wasn't possible to know if it's really there")
                while True:
                    time.sleep(1)
                
##
        elif way == "Datamatrix":
#
            if objective == "Key":
                return False
#
            elif objective == "KeyCase":
                return False
#
            elif objective == "Dropper":
                return False
     
        
##############################################################################
##                            EventsInit()                                  ##
##      A method to initialize several captors on the Nao                   ##    
##                                                                          ##

    def EventsInit(self,*_args):

        FrontTactil = ALProxy("ALMemory")
        MiddleTactil = ALProxy("ALMemory")
        RearTactil = ALProxy("ALMemory")
        IrReceiver = ALProxy("ALMemory")

        FrontTactil.subscribeToEvent("FrontTactilTouched",
                                     self.name,
                                     "start_memento")
        
        MiddleTactil.subscribeToEvent("MiddleTactilTouched",
                                      self.name,
                                      "start_maestro")
        
        RearTactil.subscribeToEvent("RearTactilTouched",
                                    self.name,
                                    "start_gato")

        IrReceiver.subscribeToEvent("InfraRedRemoteKeyReceived",
                                    self.name,
                                    "IR_receiver")


##############################################################################
##                     TactilStart() / TactilStop()                         ##
##             methods to enable or disable tactil head events              ##    
##                                                                          ##

    def TactilStart(self,*_args):

        FrontTactil.subscribeToEvent("FrontTactilTouched",
                                     self.name,
                                     "start_memento")
        
        MiddleTactil.subscribeToEvent("MiddleTactilTouched",
                                      self.name,
                                      "start_maestro")
        
        RearTactil.subscribeToEvent("RearTactilTouched",
                                    self.name,
                                    "start_gato")

    
    def TactilStop(self,*_args):

        FrontTactil.unsubscribeToEvent("FrontTactilTouched",
                                     self.name)
        
        MiddleTactil.unsubscribeToEvent("MiddleTactilTouched",
                                      self.name)
        
        RearTactil.unsubscribeToEvent("RearTactilTouched",
                                    self.name)

##############################################################################
##                            EventsInit()                                  ##
##      A method to initialize several captors on the Nao                   ##    
##                                                                          ##
        
    def IR_receiver(self, strVarName, value, strMessage):
        self.logs.display("The dropper responded")
        print "Data changed on", strVarName, ": ", value, " ", strMessage
