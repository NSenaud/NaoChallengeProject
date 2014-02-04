#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                   Nao Challenge 2014 Main Program                       # #
# ########################################################################### #
# # File: directionFromLine.py                                              # #
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
import cv2                          # OpenCV: Visual recognition library.
import vision_definitions           # Image definitions macros.

from threading import Thread        # Multithreading librairy.
from optparse import OptionParser   # Parser to keep connexion with Nao.

# Nao's libraries.
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

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
            # # Version : 2.0                                               # #
            # # Quality : -/10                                              # #
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

            elif (averageX > (imgCenter + imgWidth*0.15)):
                # Nao is on the left of the line.
                self.logs.display("< Correction Module > Nao is on the left of the line",
                                  "Warning")

            else:
                self.logs.display("< Correction Module > Nao is on the line",
                                  "Good")

            global alpha
            alpha = np.arctan(( 60.*(averageX - imgCenter)) / (65.*imgWidth))
            self.logs.display("Alpha angle (radian)",
                              "Default",
                              str(alpha))

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