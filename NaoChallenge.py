#!/usr/bin/env python
# -*- coding:Utf-8 -*-

import sys
import time
import cv2              # OpenCV: Visual recognition library.
import numpy as np      # Numpy:  Maths library.

# ---*** nao libraries ***---
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

import vision_definitions

from optparse import OptionParser


myBroker = None
followTheLine = None
memory = None
definition = vision_definitions.k4VGA


# Nao's domain name.
IP = "NaoCRIC.local"
# Nao's standard port.
port = 9559


# Class to log events.
class logs:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.INFO = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.ERROR = ''
        self.ENDC = ''

    def display(self, message, logType="Default", additionalMessage=" "):
        if ((logType == "Default") or (logType == 3)):
            print self.OKBLUE + "[ INFO ]" + self.ENDC + message + additionalMessage
        elif ((logType == "Good") or (logType == 2)):
            print self.OKGREEN + "[ INFO ]" + self.ENDC + message + additionalMessage
        elif ((logType == "Warning") or (logType == 1)):
            print self.WARNING + "[ WARNING ]" + self.ENDC + message + additionalMessage
        elif ((logType == "Error") or (logType == 0)):
            print self.ERROR + "[ ERROR ]" + self.ENDC + message + additionalMessage



class followTheLineModule(ALModule):
    """docstring for followTheLineModule"""
    def __init__(self, name):
        ALModule.__init__(self, name)
        global myBroker
        self.logs.display("Initializing module...")
        
        # Create an ALTextToSpeech proxy.
        self.tts = ALProxy("ALTextToSpeech")
        self.tts.setLanguage("french")
        self.tts.setVolume(0.3)
        self.logs.display("Subscribed to an ALTextToSpeech proxy")

        # Create an ALMotion proxy.
        self.motion = ALProxy("ALMotion")
        self.logs.display("Subscribed to an ALMotion proxy")
        
        # Create an ALMotion ALRobotPosture.
        self.posture = ALProxy("ALRobotPosture")
        self.logs.display("Subscribed to an ALRobotPosture proxy")
        
        self.posture.goToPosture("StandInit", 1.0)
        self.logs.display("Nao go to posture StandInit")

        # Create an ALLeds proxy.
        self.leds = ALProxy("ALLeds")
        self.logs.display("Subscribed to an ALLeds proxy")

        # Create an ALVideoDevice proxy.
        self.camProxy = ALProxy("ALVideoDevice")
        self.logs.display("Subscribed to an ALVideoDevice proxy")

        # Register a video module.
        colorSpace = vision_definitions.kBGRColorSpace
        fps = 10
        camera = 1      # 1 = low / 0 = high.

        self.followTheLineCam = self.camProxy.subscribeCamera("followTheLineCam",
                                                              camera,
                                                              definition,
                                                              colorSpace,
                                                              fps)
        self.logs.display("Subscribed to Camera 1")

        self.logs.display("Module ready", "Good")
        self.tts.say("Je suis prêt")

        # Call main loop.
        self.NaoFollowsTheLineMainLoop()


    # Get an image from Nao camera.
    def readNaoCam(self):
        # Get image.
        #imgNao = camProxy.getImageLocal(nameId)
        imgNAO = self.camProxy.getImageRemote(self.nameId)
        self.camProxy.releaseImage(self.nameId)
        self.logs.display("Got an image from Camera 1")

        # lire les parametres
        width = imgNAO[0]
        height = imgNAO[1]
        channels = imgNAO[2]
        imgsrc = imgNAO[6]
        # Conversion « magique » vers OpenCV
        img = np.fromstring(imgsrc, dtype="uint8").reshape(height, width, channels)
        self.logs.display("Image converted")

        return img


    def getVectorsCoordinates(self):
        img = self.readNaoCam()
        # Conversions for color (white) detection.
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # White detection.
        self.logs.display("Adding white filter")
        lower_white = np.array([0, 0, 255])
        upper_white = np.array([255,255,255])
        white = cv2.inRange(hsv_img, lower_white, upper_white)
        # Filter white on original.
        img = cv2.bitwise_and(img, img, mask=white)

        # Conversions for lines detection.
        self.logs.display("Adding lines-finder filter")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 30, 180, apertureSize=3)

        # Line detection.
        minLineLength = 100000
        maxLineGap = 5
        self.lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength, maxLineGap)

        # Write lines on image return.
        try:
            if self.lines.any():
                self.logs.display("At least one line have been detected")
                for x1,y1,x2,y2 in self.lines[0]:
                    cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

                return 0

        except AttributeError:
            self.logs.display("No line detected!", "Warning")

            return 1


    def getDirectionFromVectors(self, coordinates):
        vectors = []
        sumX = 0

        # Get vectors coordinates instead of points coordinates.
        for x1,y1,x2,y2 in coordinates[0]:
            # Compute vector's coordinates.
            y = y2-y1
            x = x2-x1
            vectors.append(np.arctan2(y, x)*360/(2*np.pi))

            # Add coordinates of points to compute average position of them to
            # know where is the line for Nao.
            sumX += x1
            sumX += x2

        self.logs.display("Converted coordinates in vectors")

        # Compute the position of the line.
        averageX = sumX/(2*len(vectors))
        self.logs.display("Average position of line:", "Default", averageX)
        
        # Correction of a positive/negative degres problem.
        for angle in xrange(0,len(vectors)):
            if (vectors[angle] < 0):
                vectors[angle] = 180 + vectors[angle]

        # Average computation.
        angleSum = 0
        for angle in xrange(0,len(vectors)):
            angleSum += vectors[angle]
            average = angleSum/len(vectors)

        self.logs.display("Line direction (degres):", "Default", average)

        # Get value in radian to give Nao a direction.
        direction = average - 90
        direction = direction*np.pi/180

        # ################### Trajectory Correction Module ################### #

        # Compute direction Nao need to take to get the line.
        global definition

        # Get image definition.
        if (definition == 3):
            imgWidth = 1280
        elif (definition ==2):
            imgWidth = 640
        else:
            self.logs.display("Definition unknown!", "Error")
            self.interruptProgram("Error")

        imgCenter = imgWidth/2
        length = averageX - imgCenter

        if (averageX < (imgCenter - imgWidth*0.15)):
            # Nao is on the right of the line.
            self.logs.display("Nao is on the right of the line", "Warning")
            direction = -0.1
        elif (averageX > (imgCenter + imgWidth*0.15)):
            # Nao is on the left of the line.
            self.logs.display("[WARNING ] Nao is on the left of the line", "Warning")
            direction = 0.1

        # ############################## End of ############################## #
        # ################### Trajectory Correction Module ################### #

        return direction

        
    # Get Nao following the line.
    def NaoFollowsTheLineMainLoop(self):
        try:
            while True:
                self.getVectorsCoordinates()
                
                try:
                    if self.lines.any():
                        self.leds.randomEyes(0.5)
                        self.leds.on("FaceLeds")
                        direction = self.getDirectionFromVectors(self.lines)

                        self.logs.display( "[INFO ] Direction (radian):", direction

                        # self.motion.post.angleInterpolation(["HeadYaw"],
                        #                                     -direction,
                        #                                     1,
                        #                                     True)

                        self.motion.moveTo(0.3, 0, direction)

                        self.logs.display("Nao is walking following the line :)")

                except AttributeError:
                    self.tts.say("Oups ! Je ne vois plus la ligne")
                    self.logs.display("No line found", "Warning")

                    self.leds.rotateEyes(0xff0000, 1, 1)
                    self.motion.killMove()

        except KeyboardInterrupt:
            self.interruptProgram("User")
            

    def interruptProgram(self, reason="User"):
        if (reason == "User"):
            self.logs.display("Interrupted by user, shutting down", "Error")
        elif (reason == "Error"):
            self.logs.display("Fatal error, shutting down", "Error")
            
        self.motion.post.angleInterpolation(["HeadYaw"],
                                             0,
                                             1,
                                             True)
        self.posture.goToPosture("Sit", 1.0)
        self.logs.display("Nao go to posture Sit")

        self.motion.setStiffnesses("Body", 0.0)
        self.logs.display("Motors shot down")
        
        self.camProxy.unsubscribe("getLineModule")
        self.logs.display("Camera unsubscribed")
        
        self.leds.on("FaceLeds")
        self.tts.say("Je suis prêt à reprendre le travail quand tu veux")
        myBroker.shutdown()

        self.logs.display("Broker unsubscribed")
        print "[ NAO IS IDLE ]"
        sys.exit(0)


# ---*** Main Function ***---
def main():
    # Create parser to maintain connexion with Nao.
    parser = OptionParser()
    parser.set_defaults(pip = IP, pport = 9559)
        
    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport

    global myBroker
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, pip, pport)

    global followTheLine
    followTheLine = followTheLineModule("followTheLine")

if __name__ == '__main__':
    main()