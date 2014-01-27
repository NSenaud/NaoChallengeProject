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

# Image definitions macros.
import vision_definitions

from optparse import OptionParser
from threading import Thread


# Constants:
mainVolume = 0.3

myBroker = None
followTheLine = None
memory = None
# Definition of the cam.
definition = vision_definitions.kVGA
# Direction (in radian) Nao should follow.
direction = 0
# Current image from the cam:
imgNAO = None


# Nao's domain name.
IP = "NaoCRIC.local"
# Nao's standard port.
port = 9559



def interruptProgram(self, reason="Error"):
    if (reason == "User"):
        self.logs.display("Interrupted by user, shutting down", "Good")
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
    
    self.leds.on("FaceLeds")
    self.tts.say("Je suis prêt à reprendre le travail quand tu veux")
    myBroker.shutdown()

    self.logs.display("Broker unsubscribed")
    self.logs.display("NAO IS IDLE", "Good")
    sys.exit(0)



# Class to log events.
class logs(object):
    def __init__(self):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.ERROR = '\033[91m'
        self.ENDC = '\033[0m'


    def display(self, message, logType="Default", additionalMessage=" "):
        if ((logType == "Default") or (logType == 3)):
            print self.OKBLUE + "[ INFO ]" + self.ENDC + message + additionalMessage
        elif ((logType == "Good") or (logType == 2)):
            print self.OKGREEN + "[ INFO ]" + self.ENDC + message + additionalMessage
        elif ((logType == "Warning") or (logType == 1)):
            print self.WARNING + "[ WARNING ]" + self.ENDC + message + additionalMessage
        elif ((logType == "Error") or (logType == 0)):
            print self.ERROR + "[ ERROR ]" + self.ENDC + message + additionalMessage



class RefreshCam(ALModule, Thread):
    """docstring for NaoWalks"""
    def __init__(self):
        Thread.__init__(self)
        ALModule.__init__(self, name)

        global imgNAO
        global myBroker
        
        # Create new object to get logs on computer's terminal.
        self.logs = logs()

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


    def run(self):
        # Get image.
        #imgNao = camProxy.getImageLocal(self.followTheLineCam)
        while True:
            imgNAO = self.camProxy.getImageRemote(self.followTheLineCam)
            self.camProxy.releaseImage(self.followTheLineCam)
            self.logs.display("Got an image from Camera 1")


    def stop(self):
        self.motion.killMove()



class getDirectionFromLine(ALModule, Thread):
    """docstring for getDirection"""
    def __init__(self):
        Thread.__init__()
        ALModule.__init__(self, name)

        self.lines = None
        
        global myBroker
        global direction

        # Create new object to get logs on computer's terminal.
        self.logs = logs()

        # Create new thread to refresh cam.
        global RefreshCam
        RefreshCam = RefreshCam()
        # Start thread.
        RefreshCam.start()

        # Create an ALLeds proxy.
        self.leds = ALProxy("ALLeds")
        self.logs.display("Subscribed to an ALLeds proxy")


    def getVectorsCoordinates(self):
        img = imgNAO

        # Read parameters.
        width = img[0]
        height = img[1]
        channels = img[2]
        imgsrc = img[6]

        # « magic » conversion to OpenCV.
        img = np.fromstring(imgsrc, dtype="uint8").reshape(height, width, channels)
        self.logs.display("Image converted")

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

        except AttributeError:
            self.logs.display("No line detected!", "Warning")


    def getDirectionFromVectors(self):
        coordinates = self.lines
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
        self.logs.display("Average position of line:", "Default", str(averageX))
        
        # Correction of a positive/negative degres problem.
        for angle in xrange(0,len(vectors)):
            if (vectors[angle] < 0):
                vectors[angle] = 180 + vectors[angle]

        # Average computation.
        angleSum = 0
        for angle in xrange(0,len(vectors)):
            angleSum += vectors[angle]
            average = angleSum/len(vectors)

        self.logs.display("Line direction (degres):", "Default", str(average))

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
            self.logs.display("Nao is on the left of the line", "Warning")
            direction = 0.1

        # ############################## End of ############################## #
        # ################### Trajectory Correction Module ################### #


    def run(self):
        self.getVectorsCoordinates()
        self.getDirectionFromVectors()


    def delete(self):
        self.camProxy.unsubscribe("followTheLineCam")
        self.logs.display("Camera unsubscribed")


class NaoWalks(ALModule, Thread):
    """docstring for NaoWalks"""
    def __init__(self):
        Thread.__init__(self)
        ALModule.__init__(self, name)
        global myBroker
        global direction
        # Create new object to get logs on computer's terminal.
        self.logs = logs()

        # Create an ALMotion proxy.
        self.motion = ALProxy("ALMotion")
        self.logs.display("Subscribed to an ALMotion proxy")


    def run(self):
        self.logs.display("Direction (radian):", "Default", str(direction))
        self.motion.moveTo(0.3, 0, direction)
        self.logs.display("Nao is walking :)", "Good")


    def stop(self):
        self.motion.killMove()
        


class followTheLineModule(ALModule, Thread):
    """docstring for followTheLineModule"""
    def __init__(self, name):
        Thread.__init__()
        ALModule.__init__(self, name)

        global myBroker
        global direction
        
        # Create new object to get logs on computer's terminal.
        self.logs = logs()
        self.logs.display("Initializing module...")
        
        # Create new threads.
        self.getDirectionFromLine = getDirectionFromLine()
        self.NaoWalks = NaoWalks()
        
        # Create an ALTextToSpeech proxy.
        self.tts = ALProxy("ALTextToSpeech")
        self.tts.setLanguage("french")
        global mainVolume
        self.tts.setVolume(mainVolume)
        self.logs.display("Subscribed to an ALTextToSpeech proxy in followTheLineModule thread")
        
        # Create an ALMotion ALRobotPosture.
        self.posture = ALProxy("ALRobotPosture")
        self.logs.display("Subscribed to an ALRobotPosture proxy")
        self.posture.goToPosture("StandInit", 1.0)
        self.logs.display("Nao go to posture StandInit")

        # Create an ALLeds proxy.
        self.leds = ALProxy("ALLeds")
        self.logs.display("Subscribed to an ALLeds proxy")

        # Ready!
        self.logs.display("Module ready", "Good")
        self.tts.say("Je suis prêt")


    def run(self):
        # Start a new threads.
        self.getDirectionFromLine.start()
        self.NaoWalks.start()

        try:
            while True:
                if (self.getDirectionFromLine.isAlive() == False):
                    # Start a new thread.
                    self.getDirectionFromLine.start()

                if (self.NaoWalks.isAlive() == False):
                    # Start a new thread.
                    self.NaoWalks.start()

                self.getVectorsCoordinates()
                
                try:
                    if self.lines.any():
                        self.leds.randomEyes(0.5)
                        self.leds.on("FaceLeds")
                        direction = self.getDirectionFromVectors(self.lines)

                except AttributeError:
                    self.tts.say("Oups ! Je ne vois plus la ligne")
                    self.logs.display("No line found", "Warning")

                    # Rotate red eyes.
                    self.leds.rotateEyes(0xff0000, 1, 1)

        except KeyboardInterrupt:
            interruptProgram("User")



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
    # Create new thread.
    followTheLine = followTheLineModule("followTheLine")
    # Start new thread.
    followTheLine.start()

if __name__ == '__main__':
    main()