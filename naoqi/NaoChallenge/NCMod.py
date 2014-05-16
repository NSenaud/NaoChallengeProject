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
import getCalendarDay

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
FlagIR = False
names = list()
times = list()
keys = list()


# Global objects:
myBroker = None                     # Broker to keep connexion with Nao. 
memory = None                       # memories objects to recall events.
FrontTactil = None                  
MiddleTactil = None
RearTactil = None
RemoteRx = None



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

        self.RedTracker = ALProxy("ALRedBallTracker")
        self.logs.display("Subscribed to an ALRedBallTracker proxy",
                          "Good")
        
        self.RemoteTx = ALProxy("ALInfrared")
        self.RemoteTx.initReception(3)
        self.logs.display("Subscribed to an ALInfrared proxy",
                          "Good")

        self.NCProxy = ALProxy("NaoChallengeGeoloc",IP,port)
        try:
            self.NCProxy.registerToVideoDevice(definition, colors)
            self.logs.display("Subscribed to an NaoChallengeGeoloc proxy",
                              "Good")
        except:
            self.logs.display("NaoChallengeGeoloc proxy already registered",
                              "Warning")

        self.NCMotion = TimelinesModule()
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
        self.logs.display("Nao is going to posture StandInit","Good")        
        
        self.EventsInit()
        self.logs.display("tactil initialisation","Good")

        # Ready!
        print ("--------------------------------------------------------------------------")
        print ("--------------------------------------------------------------------------")
        self.logs.display("Module ready", "Good")


##############################################################################
##                            start_memento()                               ##
##                    A method to launch memento mod                        ##    
##                                                                          ##

    def start_memento (self,*_args):

        self.TactilStop()
        
        # Walk to the Door
        self.tts.post.say("je m'occupe de la clef")
        self.logs.display("Going to the Door")
        try:
            self.NCProxy.registerToVideoDevice(definition, colors)
        except:
            self.logs.display("NaoChallengeGeoloc proxy already registered","Warning")
        self.NCProxy.walkFromDmtxToDmtx(270,220)
        self.NCProxy.unRegisterFromVideoDevice()
        
        # Aim the key
        self.RedTracker.startTracker()
        while self.RedTracker.getPosition() == [0.0, 0.0, 0.0]:
            self.logs.display("The key isn't visible")
            while self.RedTracker.getPosition() == [0.0, 0.0, 0.0]:
                time.sleep(0.01)
        self.logs.display("The key is visible")

        # Get the Key
        while self.GetObject("Key","RedDetection") != True :
            time.sleep(3)

        # Unplug the key
        self.logs.display("Going to the Key Case") 
        self.leftArmEnable  = True
        self.rightArmEnable  = False
        self.motion.setWalkArmsEnabled(self.leftArmEnable, self.rightArmEnable)
        self.motion.moveTo(-0.3 , 0.0 , 0.0)
       
        # Walk where the Key is suppose to be
        self.NCProxy.registerToVideoDevice(definition, colors)
        self.NCProxy.walkFromDmtxToDmtx(220,290)
        self.logs.display("Key Case Reach")        

        # Aim the box
        try:
            motion.angleInterpolation(["HeadPitch"], [[ 0.0]], [[ 0.5]], True);
        except BaseException, err:
            print err
        self.RedTracker.startTracker()
        while self.RedTracker.getPosition() == [0.0, 0.0, 0.0]:
            self.logs.display("The key isn't visible")
            while self.RedTracker.getPosition() == [0.0, 0.0, 0.0]:
                time.sleep(0.01)
        self.logs.display("The key is visible")

        # Drop the Key
        while self.GetObject("KeyCase","RedDetection") != True :
            time.sleep(3)
        self.motion.moveTo(-0.5, 0.0, 0.0)

        # Exit ...
        rightArmEnable  = True
        self.motion.setWalkArmsEnabled(leftArmEnable, rightArmEnable)
        self.NCProxy.unRegisterFromVideoDevice()
        log.display("sits down")
        NaoChallenge.posture.goToPosture("Crouch", 1.0)
        NaoChallenge.motion.setStiffnesses("Body", 0.0)
        self.TactilStart()



##############################################################################
##                            start_maestro()                               ##
##                    A method to launch maestro mod                        ##    
##                                                                          ##
    def start_maestro (self,*_args):

        self.TactilStop()

        # Walk to the Calendar
        self.tts.post.say("quel jour sommes nous aujourd'hui ?")
        self.logs.display("Go to the Calendar")
        try:
            self.NCProxy.registerToVideoDevice(definition, colors)
        except:
            self.logs.display("NaoChallengeGeoloc proxy already registered","Warning")
        self.NCProxy.walkFromDmtxToDmtx(270, 210)
        self.logs.display("Calendar Reach")

        # Read the Calendar
        try:
            self.day = getCalendarDay.maestroReading()
        except Exception,e:
            print e

        # Act depending on the day
        self.FunnyActions(str(self.day))

        # Exit ...
        self.NCProxy.unRegisterFromVideoDevice()
        log.display("sits down")
        NaoChallenge.posture.goToPosture("Crouch", 1.0)
        NaoChallenge.motion.setStiffnesses("Body", 0.0)
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
        #self.motion.moveTo(0.5, 0, 0)
        self.logs.display("Dropper Reach")

        # Turn it On
        RemoteRx.subscribeToEvent("InfraRedRemoteKeyReceived",
                                     self.name,
                                     "IR_receiver")
        while (FlagIR == False):

            self.RemoteTx.sendRemoteKey("Sony_RM-ED009-12", "info")
            self.logs.display("info message send")
            time.sleep(1)

            pass

        FlagIR = False

        while (FlagIR == False | 
            RemoteRx.getData("Device/SubDeviceList/IR/LIRC/Remote/Key/Sensor/Value/") != "power"):

            self.RemoteTx.sendRemoteKey("Sony_RM-ED009-12", "power")
            self.logs.display("power message send")
            time.sleep(1)

            pass
            

        self.logs.display("Dropper activated")

        
        log.display("sits down")
        NaoChallenge.posture.goToPosture("Crouch", 1.0)
        NaoChallenge.motion.setStiffnesses("Body", 0.0)
        self.TactilStart()

##############################################################################
##                        FunnyActions("day")                               ##
##      A method to say something linked to the day                         ##    


    def FunnyActions(self, day = "Lundi"):

        if day == "Lundi":
            self.tts.say("La semaine vient juste de commencer, mais il y à déja tant de chose à faire.")

        elif day == "Mardi":
            self.tts.say("L'anniversaire de Roméo c'est jeudi soir prochain, cela me laisse deux petit jour pour lui trouver un cadeau !")

        elif day == "Mercredi":
            self.tts.say("Oh, c'est Mercredi, le jour du vétérinaire d'asrael !")

        elif day == "Jeudi":
            self.tts.say("Aujourd'hui c'est l'anniversaire de Roméo ! j'espère que son cadeau lui plaira.")

        elif day == "Vendredi":
            self.tts.say("Les Capulets, viennent manger ce soir. Il faut préparer le repas.")

        elif day == "Samedi":
            self.tts.say("Youpi, c'est le début du week-end !")

        elif day == "Dimanche":
            self.tts.say("Oh, mince alors, le week-end est bientôt fini.")

##############################################################################
##                  GetObject("objective", "way")                           ##
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
        global names
        global times
        global keys

        if way == "RedDetection":
            
            # locate the red ball on the screen
            self.RedTracker.startTracker()
            time.sleep(1)
            self.pos = self.RedTracker.getPosition()
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
                    try:             
                        while self.distance > 0.29: 
                            # Get sonars echos
                            self.LeftSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
                            self.RightSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
                            self.distance = (self.LeftSonar + self.RightSonar)/2.0
                            time.sleep(0.1)
                            self.head = self.motion.getAngles("Head",True)
                            self.head.reverse()
                            self.headyaw = self.head.pop()
                            self.motion.moveToward(0.7, 0, self.headyaw/2.5)

                            #if self.RedTracker.isNewData():
                                #self.logs.display("Distance from the key in cm")
                                #self.logs.display(100*self.distance)

                        self.logs.display("Door reached")
                        self.motion.stopMove()

                        

                        #get even closer
                        for self.r in range(2):
                            time.sleep(1)
                            self.head = self.motion.getAngles("Head",True)
                            self.head.reverse()
                            self.headyaw = self.head.pop()
                            leftArmEnable  = True
                            rightArmEnable  = False
                            self.motion.setWalkArmsEnabled(leftArmEnable, rightArmEnable)
                            self.motion.moveTo(0.04, self.headyaw/10 + 0.03, 0.06)
                        
                    except:
                        print "bug" 
                       
                    self.NCMotion.GetTheKey()   # this line use a method in timelines.py which provide tables used after
                    self.motion.angleInterpolation(names, keys, times, True)
                    time.sleep(1)


                    #self.motion.openHand("RHand")
                    X = -0.1
                    V = 0.03
                    self.errors = 0

                    while self.errors<0.04:

                        if X>0:
                            V= -0.03
                        elif X< -1.2:
                            V=0.03
                        self.motion.angleInterpolation(["RShoulderRoll"], [[X]], [[0.1]], True)
                        time.sleep(0.1)
                        X= V+X

                        
                        self.joint = "RShoulderRoll"
                        self.useSensors    = False
                        self.commandAngles = self.motion.getAngles(self.joint, self.useSensors)
                        #print "Command angles:"
                        #print str(self.commandAngles)
                        #print ""

                        self.useSensors  = True
                        self.sensorAngles = self.motion.getAngles(self.joint, self.useSensors)
                        #print "Sensor angles:"
                        #print str(self.sensorAngles)
                        #print ""

                        for self.i in range(0, len(self.commandAngles)):
                            self.errors = (self.commandAngles[self.i]-self.sensorAngles[self.i])
                        #print "Errors"
                        #print self.errors

                        pass

                    self.RedTracker.stopTracker()
                    A = list()
                    B = list()
                    C = list()
                    A.append("RHand")
                    C.append([ 0.001, 1.0])
                    B.append([ 1.0, 0.0])
                    self.motion.angleInterpolation(A, B, C, True)
                    #self.motion.closeHand("RHand")
                    time.sleep(4)
                    
                    return True
#                   
                elif objective == "KeyCase":

                    for self.n in range(3):       
                        # Get sonars echos
                        #self.LeftSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
                        #self.RightSonar = self.memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
                        #self.distance = (self.LeftSonar + self.RightSonar)/2.0
                        time.sleep(2)
                        self.head = self.motion.getAngles("Head",True)
                        self.head.reverse()
                        self.headyaw = self.head.pop()
                        self.motion.moveToward(0.7, 0.3, self.headyaw*3)                        
                        pass

                    self.motion.stopMove()
############################
                    self.tts.say("suis-je bien face à la boîte ?")
                    time.sleep(3)
############################   

                    self.NCMotion.DropTheKey()   # this line use a method in timelines.py which provide tables used after
                    
                    self.motion.angleInterpolation(names, keys, times, True)

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
                        
                        if self.RedTracker.isNewData():
                            self.motion.moveToward(0.7, 0, self.headyaw/2.0)
                            self.logs.display("Distance from the key in cm")
                            self.logs.display(100*self.distance)
                    self.motion.stopMove()
                    self.motion.moveTo(0.05, 0, 0)           
                    
                    self.NCMotion.PressTheButton()   # this line use a method in timelines.py which provide tables used after
                    
                    self.motion.angleInterpolation(names, keys, times, True)

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

    def EventsInit(self):
        global FrontTactil
        global MiddleTactil
        global RearTactil
        global RemoteRx
        

        FrontTactil = ALProxy("ALMemory")
        MiddleTactil = ALProxy("ALMemory")
        RearTactil = ALProxy("ALMemory")
        RemoteRx = ALProxy("ALMemory")


        FrontTactil.subscribeToEvent("FrontTactilTouched",
                                     self.name,
                                     "start_memento")
        
        MiddleTactil.subscribeToEvent("MiddleTactilTouched",
                                      self.name,
                                      "start_maestro")
        
        RearTactil.subscribeToEvent("RearTactilTouched",
                                    self.name,
                                    "start_gato")

        RemoteRx.subscribeToEvent("InfraRedRemoteKeyReceived",
                                    self.name,
                                    "IR_receiver")


##############################################################################
##                     TactilStart() / TactilStop()                         ##
##             methods to enable or disable tactil head events              ##    
##                                                                          ##

    def TactilStart(self):

        FrontTactil.subscribeToEvent("FrontTactilTouched",
                                     self.name,
                                     "start_memento")
        
        MiddleTactil.subscribeToEvent("MiddleTactilTouched",
                                      self.name,
                                      "start_maestro")
        
        RearTactil.subscribeToEvent("RearTactilTouched",
                                    self.name,
                                    "start_gato")

    
    def TactilStop(self):

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
        
    def IR_receiver(self, *_args):
        self.logs.display("The dropper responded")
        self.logs.display( memory.getData("Device/SubDeviceList/IR/LIRC/Remote/Key/Sensor/Value/") )
        FlagIR = True







class TimelinesModule():
    def __init__(self):
        global names
        global times
        global keys

    def GetTheKey(self):

        global names
        global times
        global keys
        
        del names[:]
        del times[:]
        del keys[:]

        names.append("LElbowRoll")
        times.append([ 0.36000, 0.80000])
        keys.append([ -0.50925, -0.50925])

        names.append("LElbowYaw")
        times.append([ 0.36000, 0.80000])
        keys.append([ -1.48035, -1.48035])

        names.append("LHand")
        times.append([ 0.36000, 0.80000])
        keys.append([ 1.0, 1.0])

        names.append("LShoulderPitch")
        times.append([ 0.36000, 0.80000])
        keys.append([ 1.81008, 1.81008])

        names.append("LShoulderRoll")
        times.append([ 0.36000, 0.80000])
        keys.append([ 0.17483, 0.17483])

        names.append("LWristYaw")
        times.append([ 0.36000, 0.80000])
        keys.append([ -0.00004, -0.00004])

        names.append("RElbowRoll")
        times.append([ 0.36000, 0.80000])
        keys.append([ 1.49876, 1.19503])

        names.append("RElbowYaw")
        times.append([ 0.36000, 0.80000])
        keys.append([ 1.15199, 0.88814])

        names.append("RHand")
        times.append([ 0.36000, 0.80000])
        keys.append([ 1.0, 1.0])

        names.append("RShoulderPitch")
        times.append([ 0.36000, 0.80000])
        keys.append([ 0.14731, -0.35])

        names.append("RShoulderRoll")
        times.append([ 0.36000, 0.80000])
        keys.append([ -1.16742, -0.1])

        names.append("RWristYaw")
        times.append([ 0.36000, 0.80000])
        keys.append([ 0.07973, 0.03371])




    def DropTheKey(self):

        global names
        global times
        global keys
        
        del names[:]
        del times[:]
        del keys[:]

        names.append("RElbowRoll")
        times.append([ 0.5, 4.0])
        keys.append ([ 1.5, 0.6])

        names.append("RElbowYaw")
        times.append([ 0.5, 4.0])
        keys.append ([ 1.2, -1.3])

        names.append("RHand")
        times.append([ 0.5, 4.0, 4.5])
        keys.append ([ 0.0, 0.0, 1.0])

        names.append("RShoulderPitch")
        times.append([ 0.5, 4.0])
        keys.append ([ 0.1, -0.0])

        names.append("RShoulderRoll")
        times.append([ 0.5, 4.0])
        keys.append ([ -1.2, -0.0])

        names.append("RWristYaw")
        times.append([ 0.5, 4.0])
        keys.append ([ 0.1, 1.8])



#    def PressTheButton(self):

