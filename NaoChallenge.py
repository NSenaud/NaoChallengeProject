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

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


class followTheLineModule(ALModule):
    """docstring for followTheLineModule"""
    def __init__(self, name):
        ALModule.__init__(self, name)
        global myBroker
        print "[INFO ] 'followTheLineModule' initializing..."
        
        # Create an ALTextToSpeech proxy.
        self.tts = ALProxy("ALTextToSpeech")
        self.tts.setLanguage("french")
        self.tts.setVolume(0.3)
        print "[INFO ] Subscribed to an ALTextToSpeech proxy"
        # Create an ALMotion proxy.
        self.motion = ALProxy("ALMotion")
        print "[INFO ] Subscribed to an ALMotion proxy"
        # Create an ALMotion ALRobotPosture.
        self.posture = ALProxy("ALRobotPosture")
        print "[INFO ] Subscribed to an ALRobotPosture proxy"
        self.posture.goToPosture("StandInit", 1.0)
        print "[INFO ] Nao go to posture StandInit"
        # Create an ALLeds proxy.
        self.leds = ALProxy("ALLeds")
        # Create an ALVideoDevice proxy.
        self.camProxy = ALProxy("ALVideoDevice")
        print "[INFO ] Subscribed to an ALVideoDevice proxy"
        # Register a video module.
        colorSpace = vision_definitions.kBGRColorSpace
        fps = 5
        camera = 1 # 1 = bas / 0 = haut.

        self.nameId = self.camProxy.subscribeCamera("getLineModule",
                                                    camera,
                                                    definition,
                                                    colorSpace,
                                                    fps)
        print "[INFO ] Subscribed to Camera 1"

        print "[INFO ] 'followTheLineModule' initialized"

        self.tts.say("Je suis ton esclave, Impératrice, fais-moi ce que tu veux !")
        self.NaoFollowsTheLine()

    # Get an image from Nao camera.
    def readNaoCam(self):
        # Get image.
        #img = camProxy.getImageLocal(nameId)
        imgNAO = self.camProxy.getImageRemote(self.nameId)
        print "[INFO ] Got an image from Camera 1"
        self.camProxy.releaseImage(self.nameId)

        print "[INFO ] Converting image..."
        # lire les parametres
        width = imgNAO[0]
        height = imgNAO[1]
        channels = imgNAO[2]
        imgsrc = imgNAO[6]
        # Conversion « magique » vers OpenCV
        img = np.fromstring(imgsrc, dtype="uint8").reshape(height,
                                                           width,
                                                           channels)
        print "[INFO ] Image converted"

        return img

    def getVectorsCoordinates(self):
        img = self.readNaoCam()

        # Conversions for color (white) detection.
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # White detection.
        print "[INFO ] Adding white filter"
        lower_white = np.array([0, 0, 255])
        upper_white = np.array([255,255,255])
        white = cv2.inRange(hsv_img, lower_white, upper_white)

        # Filter white on original.
        img = cv2.bitwise_and(img, img, mask= white)

        # Conversions for lines detection.
        print "[INFO ] Adding lines filter"
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray,30,180,apertureSize = 3)

        minLineLength = 100000
        maxLineGap = 5
        # Line detection.
        self.lines = cv2.HoughLinesP(edges,
                                     1,
                                     np.pi/180,
                                     100,
                                     minLineLength,
                                     maxLineGap)

        # Write lines on image return.
        try:
            if self.lines.any():
                print "[INFO ] At least one line have been detected"
                for x1,y1,x2,y2 in self.lines[0]:
                    cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
        except AttributeError:
            print "[WARNING ] No line detected!"


    def getDirectionFromVectors(self, coordinates):
        vectors = []
        sumX = 0

        # Get vectors coordinates instead of points coordinates.
        print "[INFO ] Converting coordinates in vectors"
        for x1,y1,x2,y2 in coordinates[0]:
            # Compute vector's coordinates.
            y = y2-y1
            x = x2-x1
            vectors.append(np.arctan2(y, x)*360/(2*np.pi))

            # Add coordinates of points to compute average position of them to
            # know where is the line for Nao.
            sumX += x1
            sumX += x2

        print "[INFO ] Converted coordinates in vectors"

        averageX = sumX/(2*len(vectors))

        print "[INFO ] Average position of line:", averageX
        
        # Correction of a positive/negative degres problem.
        for angle in xrange(0,len(vectors)):
            if (vectors[angle] < 0):
                vectors[angle] = 180 + vectors[angle]

        # Average computation.
        print "[INFO ] Computing direction..."
        angleSum = 0
        for angle in xrange(0,len(vectors)):
            angleSum += vectors[angle]
            average = angleSum/len(vectors)

        print "[INFO ] Line direction (degres):", average

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
            print "[ERROR ] Definition unknown!"

        imgCenter = imgWidth/2
        length = averageX - imgCenter

        if (averageX < (imgCenter - imgWidth*0.15)):
            # Nao is on the right of the line.
            print "[WARNING ] Nao is on the right of the line"
            direction = -0.1
            # if (direction > 0):
            #     direction = -direction # Objective: get Nao back on the line.
            # elif (direction < 0):
            #     direction = 0
        elif (averageX > (imgCenter + imgWidth*0.15)):
            # Nao is on the left of the line.
            print "[WARNING ] Nao is on the left of the line"
            direction = 0.1
            # if (direction < 0):
            #     direction = -direction # Objective: get Nao back on the line.
            # elif (direction > 0):
            #     direction = 0

        # ############################## End of ############################## #
        # ################### Trajectory Correction Module ################### #

        return direction

        
    # Get Nao following the line.
    def NaoFollowsTheLine(self):
        try:
            while True:
                self.getVectorsCoordinates()
                
                try:
                    if self.lines.any():
                        print "[INFO ] Nao should walk"
                        self.leds.randomEyes(0.5)
                        self.leds.on("FaceLeds")
                        direction = self.getDirectionFromVectors(self.lines)

                        print "[INFO ] Direction (radian):", direction

                        # self.motion.post.angleInterpolation(["HeadYaw"],
                        #                                     -direction,
                        #                                     1,
                        #                                     True)

                        self.motion.moveTo(0.4, 0, direction)

                        print "[INFO ] Nao is walking following the line :)"

                except AttributeError:
                    self.tts.say("Oh oui ! Fais-moi mal !")
                    print "[WARNING ] No line to follow: Nao stopped!"
                    self.tts.say("Je ne trouve pas la ligne")
                    self.leds.rotateEyes(0xff0000, 1, 1)
                    self.motion.killMove()

                time.sleep(0.2)

        except KeyboardInterrupt:
            print "[INFO ] Interrupted by user, shutting down"
            self.motion.post.angleInterpolation(["HeadYaw"],
                                                 0,
                                                 1,
                                                 True)
            self.posture.goToPosture("Sit", 1.0)
            print "[INFO ] Nao go to posture Sit"
            self.motion.setStiffnesses("Body", 0.0)
            print "[INFO ] Motors shot down"
            self.camProxy.unsubscribe("getLineModule")
            print "[INFO ] Camera unsubscribed"
            self.leds.on("FaceLeds")
            self.tts.say("Je suis prêt à reprendre le travail quand tu veux, Impératrice !")
            myBroker.shutdown()
            print "[INFO ] Broker unsubscribed"
            print "[NAO IS IDLE ]"
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

    # Loop while...
    try:
        while True:
            time.sleep(1)

    # ... Keyboard interruption.
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)

if __name__ == '__main__':
    main()