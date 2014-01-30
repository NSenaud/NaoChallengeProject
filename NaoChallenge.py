#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                   Nao Challenge 2014 Main Program                       # #
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
import cv2                          # OpenCV: Visual recognition library.
import vision_definitions           # Image definitions macros.

from threading import Thread        # Multithreading librairy.
from optparse import OptionParser   # Parser to keep connexion with Nao.

# Nao's libraries.
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule


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
memory = None                       # A memory object to recall events.

# Global variables:
imgNAO = None                       # Current image from the cam.
direction = 0                       # Direction (in radian) Nao should follow.
directions = []
directions.append(-10)



# ######################### CLASS TO LOG EVENTS ############################# #

class logs(object):
    def __init__(self):
        # Colors definition with ASCII extended codes.
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARNING = '\033[93m'
        self.ERROR = '\033[91m'
        self.ENDC = '\033[0m'


    # Display a colored message on computer's terminal.
    def display(self, message, logType="Default", additionalMessage=" "):
        if ((logType == "Default") or (logType == 3)):
            print self.OKBLUE  + "[ INFO ]"    + self.ENDC,
            print message,
            print additionalMessage
        elif ((logType == "Good") or (logType == 2)):
            print self.OKGREEN + "[ INFO ]"    + self.ENDC,
            print message,
            print additionalMessage
        elif ((logType == "Warning") or (logType == 1)):
            print self.WARNING + "[ WARNING ]" + self.ENDC,
            print message,
            print additionalMessage
        elif ((logType == "Error") or (logType == 0)):
            print self.ERROR   + "[ ERROR ]"   + self.ENDC,
            print message,
            print additionalMessage

# ############################### END OF CLASS ############################## #



# ########################## CLASS TO REFRESH CAM ########################### #

class RefreshCam(ALModule, Thread):
    """docstring for NaoWalks"""
    def __init__(self, name):
        Thread.__init__(self)
        ALModule.__init__(self, name)

        # Create new object to get logs on computer's terminal.
        self.logs = logs()

        # Create an ALVideoDevice proxy.
        self.camProxy = ALProxy("ALVideoDevice")
        self.logs.display("Subscribed to an ALVideoDevice proxy", "Good")

        # Register a video module.
        colorSpace = vision_definitions.kBGRColorSpace
        fps = 1
        camera = 1      # 1 = mouth camera / 0 = front camera.
        self.followTheLineCam = self.camProxy.subscribeCamera("LowCam",
                                                              camera,
                                                              definition,
                                                              colorSpace,
                                                              fps)
        self.logs.display("Subscribed to Camera 1", "Good")


    # Method called by the Thread.start() method.
    def run(self):
        while True:
            global AnalyseANewPict
            if (AnalyseANewPict is True):
                global imgNAO
                # Get the image.
                imgNAO = self.camProxy.getImageRemote(self.followTheLineCam)
                self.camProxy.releaseImage(self.followTheLineCam)
                self.logs.display("Received a picture from Camera 1")

            time.sleep(1)


    # Method called to properly delete the thread.
    def delete(self):
        self.camProxy.unsubscribe("LowCam")
        self.logs.display("Camera unsubscribed", "Good")

# ############################### END OF CLASS ############################## #



# ###################### CLASS TO COMPUTE A DIRECTION ####################### #

class getDirectionFromLine(ALModule, Thread):
    """docstring for getDirection"""
    def __init__(self, name):
        Thread.__init__(self)
        ALModule.__init__(self, name)

        self.lines = None                  # Lines found by OpenCV on picts.

        # Create new object display a colored message on computer's terminal.
        self.logs = logs()


    # Find white line(s) on pict and save points' coordinates.
    def getVectorsCoordinates(self):
        global imgNAO
        img = imgNAO                        # Get the last pict from cam.

        try:
            # Read parameters.
            width = img[0]
            height = img[1]
            channels = img[2]
            imgsrc = img[6]

            # « magical » conversion to OpenCV.
            img = np.fromstring(imgsrc, dtype="uint8").reshape(height,
                                                               width,
                                                               channels)
            self.logs.display("Cam's pict converted for OpenCV")

            # Conversions for color (white) detection.
            hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # White detection.
            lower_white = np.array([0, 0, 255])
            upper_white = np.array([255,255,255])
            white = cv2.inRange(hsv_img, lower_white, upper_white)
            # Filter white on original.
            img = cv2.bitwise_and(img, img, mask=white)
            self.logs.display("< OpenCV > Added 'white only' filter")

            # Conversions for lines detection.
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 30, 180, apertureSize=3)

            # Line detection.
            minLineLength = 100000
            maxLineGap = 5
            self.lines = cv2.HoughLinesP(edges,
                                         1,
                                         np.pi/180,
                                         100,
                                         minLineLength,
                                         maxLineGap)
            self.logs.display("< OpenCV > Added 'lines finder' filter")

            # Write lines on image return.
            try:
                if self.lines.any():
                    for x1,y1,x2,y2 in self.lines[0]:
                        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

                    self.logs.display("At least one line have been found",
                                      "Good")

            except AttributeError:
                self.logs.display("No line have been found!", "Warning")
        
        except TypeError:
            self.logs.display("No pict received from cam!", "Warning")
        

    # Find direction of vectors from points' coordinates.
    def getDirectionFromVectors(self):
        global direction
        coordinates = self.lines
        vectors = []
        sumX = 0

        try:
            # Get vectors coordinates instead of points coordinates.
            for x1,y1,x2,y2 in coordinates[0]:
                # Compute vector's coordinates.
                y = y2-y1
                x = x2-x1
                vectors.append(np.arctan2(y, x)*360/(2*np.pi))

                # Add coordinates of points to compute average position of
                # them to know where is the line for Nao.
                sumX += x1
                sumX += x2

            self.logs.display("Converted line(s)' coordinates in vectors")

            # Compute the average position of the line.
            averageX = sumX/(2*len(vectors))
            self.logs.display("Average position of line:",
                              "Default",
                              str(averageX))
            
            # Correction of a positive/negative degres problem.
            for angle in xrange(0,len(vectors)):
                if (vectors[angle] < 0):
                    vectors[angle] = 180 + vectors[angle]

            # Average computation.
            angleSum = 0
            for angle in xrange(0,len(vectors)):
                angleSum += vectors[angle]
                average = angleSum/len(vectors)

            if (average > 85 or average < 95):
                self.logs.display("Line direction (degres):",
                                  "Default",
                                  str(average))

            # Get value in radian to give Nao a direction.
            direction = average - 90
            direction = direction*np.pi/180

            # ################ Trajectory Correction Module ################# #
            # # Version : 1.1                                               # #
            # # Quality : 2/10                                              # #
            # ############################################################### #

            # Compute direction Nao need to take to get the line.
            global definition
            # Get image definition.
            if (definition == 3):
                imgWidth = 1280
            elif (definition == 2):
                imgWidth = 640
            elif (definition == 1):
                imgWidth = 320
            else:
                self.logs.display("< Correction Module > Definition unknown!",
                                  "Error")

            imgCenter = imgWidth/2
            length = averageX - imgCenter

            if (averageX < (imgCenter - imgWidth*0.15)):
                # Nao is on the right of the line.
                self.logs.display("< Correction Module > Nao is on the right of the line",
                                  "Warning")
                direction = -0.1

            elif (averageX > (imgCenter + imgWidth*0.15)):
                # Nao is on the left of the line.
                self.logs.display("< Correction Module > Nao is on the left of the line",
                                  "Warning")
                direction = 0.1

            else:
                self.logs.display("< Correction Module > Nao is on the line",
                                  "Good")

            # ########################### End of ############################ #
            # ################ Trajectory Correction Module ################# #
            
            global NaoShouldWalk
            NaoShouldWalk = True
            self.logs.display("Nao should walk!", "Good")

        except TypeError:
            global NaoShouldWalk
            NaoShouldWalk = False
            self.logs.display("Nao should stop!", "Error")

        # Delete the thread.
        getDirectionFromLineThread = None

        global AnalyseANewPict
        AnalyseANewPict = True


    # Method called by the Thread.start() method.
    def run(self):
        global AnalyseANewPict
        AnalyseANewPict = False
        self.getVectorsCoordinates()
        self.getDirectionFromVectors()


    # Method called to properly delete the thread.
    def delete(self):
        pass

# ############################### END OF CLASS ############################## #



# ####################### CLASS TO CONTOL NAO'S WALK ######################## #

class NaoWalks(ALModule, Thread):
    """docstring for NaoWalks"""
    def __init__(self, name):
        Thread.__init__(self)
        ALModule.__init__(self, name)

        # Create new object display a colored message on computer's terminal.
        self.logs = logs()

        # Create an ALMotion proxy.
        self.motion = ALProxy("ALMotion")
        self.logs.display("Subscribed to an ALMotion proxy", "Good")


    # Method called by the Thread.start() method.
    def run(self):
        global direction
        global directions
        if (direction != directions.pop()):
            directions.append(direction)

            self.stop()

            self.logs.display("Nao is walking in direction (radian):",
                              "Default",
                              str(direction))
            self.motion.moveTo(0.2, 0, direction)

        global AnalyseANewPict
        AnalyseANewPict = True


    # Method called to stop Nao.
    def stop(self):
        self.motion.killMove()


    # Method called to properly delete the thread.
    def delete(self):
        self.motion.killMove()

# ############################### END OF CLASS ############################## #
        


# ######################## MAIN CLASS AND MAIN LOOP ######################### #

class followTheLineModule(ALModule, Thread):
    """docstring for followTheLineModule"""
    def __init__(self, name):
        Thread.__init__(self)
        ALModule.__init__(self, name)

        # Create new object display a colored message on computer's terminal.
        self.logs = logs()
        self.logs.display("Initializing module...")
        
        # Create new proxies.
        global mainVolume
        self.tts = ALProxy("ALTextToSpeech")
        self.tts.setLanguage("french")
        self.tts.setVolume(mainVolume)
        self.logs.display("Subscribed to an ALTextToSpeech proxy",
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

        # Create new threads.
        global getDirectionFromLineThread
        if (getDirectionFromLineThread is None):
            getDirectionFromLineThread = getDirectionFromLine("getDirectionFromLine")
            self.logs.display("New thread 'getDirectionFromLine' created",
                              "Good")

        global NaoWalksThread
        if (NaoWalksThread is None):
            NaoWalksThread = NaoWalks("NaoWalks")
            self.logs.display("New thread 'NaoWalks' created",
                              "Good")

        global RefreshCamThread
        if (RefreshCamThread is None):
            RefreshCamThread = RefreshCam("RefreshCam")
            self.logs.display("New thread 'RefreshCam' created",
                              "Good")

        # Start thread.
        if (RefreshCamThread is not None and RefreshCamThread.isAlive()):
            pass
        else:
            RefreshCamThread.start()
            self.logs.display("Thread 'RefreshCam' started",
                              "Good")

        # Ready!
        self.logs.display("Module ready", "Good")
        self.tts.say("Je suis prêt")


    # Shut down Nao by clicking on his front head button.
    def onTouched(self, *_args):
        global memory
        memory.unsubscribeToEvent("FrontTactilTouched",
                                  "followTheLine")

        # Properly close threads.
        global getDirectionFromLineThread
        getDirectionFromLineThread.delete()
        global NaoWalksThread
        NaoWalksThread.delete()
        global RefreshCamThread
        RefreshCamThread.delete()
        global followTheLine
        followTheLine.delete()


    # Method called by the Thread.start() method.
    def run(self):
        global memory       
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("FrontTactilTouched",
                                "followTheLine",
                                "onTouched")

        # Start a new threads.
        global getDirectionFromLineThread
        getDirectionFromLineThread.start()

        while True:
            if (getDirectionFromLine is not None 
                and getDirectionFromLineThread.isAlive()):
                pass
            else:
                # Start a new thread.
                getDirectionFromLineThread = getDirectionFromLine("getDirectionFromLine")
                getDirectionFromLineThread.start()

            global NaoWalksThread
            global NaoShouldWalk
            if (NaoShouldWalk is True):
                self.leds.randomEyes(0.5)
                self.leds.on("FaceLeds")
                if (NaoWalksThread.isAlive() is not True):
                    # Start a new thread.
                    NaoWalksThread = NaoWalks("NaoWalks")
                    NaoWalksThread.start()

            else:
                self.tts.say("Je recherche la ligne")
                self.logs.display("No line found", "Warning")

                NaoWalksThread.stop()
                # if (NaoWalksThread is None or NaoWalksThread.isAlive() is not True):
                #     NaoWalksThread.stop()

                # Rotate red eyes.
                self.leds.rotateEyes(0xff0000, 1, 1)

            time.sleep(1)


    # Method called to properly delete the thread.
    def delete(self):
        global myBroker
        self.motion.post.angleInterpolation(["HeadYaw"],
                                             0,
                                             1,
                                             True)
        self.posture.goToPosture("Crouch", 1.0)
        self.logs.display("Nao go to posture Crouch")

        self.motion.setStiffnesses("Body", 0.0)
        self.logs.display("Motors shot down")

        self.leds.on("FaceLeds")
        self.tts.say("Je suis prêt à reprendre le travail quand tu veux")
        myBroker.shutdown()

        self.logs.display("Broker unsubscribed")
        self.logs.display("NAO IS IDLE", "Good")
        sys.exit(0)

# ############################### END OF CLASS ############################## #



# ############################## MAIN FUNCTION ############################## #

def main():
    # Create parser to keep in touch with Nao.
    parser = OptionParser()
    parser.set_defaults(pip = IP, pport = port)
    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport

    global myBroker
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, pip, pport)

    global followTheLine
    # Create new thread.
    followTheLine = followTheLineModule("followTheLine")
    # Start the new thread.
    followTheLine.start()

# ############################### END FUNCTION ############################## #



# ############################## PROGRAM ENTRY ############################## #

if __name__ == '__main__':
    main()

# ############################### END OF FILE ############################### #