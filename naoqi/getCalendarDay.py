#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: getCalendarDay.py                                                 # #
# ########################################################################### #
# # Creation:   2014-04-07                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   # #
# #                                                                         # #
# ########################################################################### #
"""
    get Calendar weekday in Masetro trial of Nao Challenge 2014.
"""

import sys
import time
import numpy as np                  # Numpy:  Maths library.
import cv2                          # OpenCV: Visual recognition library.
import vision_definitions           # Image definitions macros.
import subprocess                   # Used to call bash scripts.

# Nao's libraries.
from naoqi import ALProxy

IP = "NaoCRIC.local"
Port = 9559
weekdays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
oldAngle = 0 # Global to keep in mind


camProxy = ALProxy("ALVideoDevice", IP, Port)
TTSProxy = ALProxy("ALTextToSpeech", IP, Port)

# Register a video module.
colorSpace = vision_definitions.kBGRColorSpace    # OpenCV sadly does not support YUV.
definition = vision_definitions.k4VGA             # Resolution Max.
fps = 3         # We can't really expect more than 2 treatment per second.
camera = 0      # 1 = mouth camera / 0 = front camera.

readCalendarCam = camProxy.subscribeCamera("CalendarCam",
                                            camera,
                                            definition,
                                            colorSpace,
                                            fps)


# Thanks to http://hetland.org/coding/python/levenshtein.py
def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def verification(proposition):
    "Find the clothest weekday from proposition or return False"

    global weekdays
    bestDay = [None, 1000]  # [ Day, matchCoeff ]

    for day in weekdays:
        match = levenshtein(day, proposition)
        if match == 1:
            return day
        elif match < bestDay[1]:
            bestDay[0] = day
            bestDay[1] = match

    if bestDay[1] < 7 and len(bestDay[0]) > 5:
        return bestDay[0]
    elif bestDay[1] < 5:
        return bestDay[0]
    else:
        return False


def rotate(img, angle):
    "Rotate 'img' of 'angle' degrees"

    global colorSpace
    if definition == vision_definitions.k4VGA:
        center = (640, 480)
    else:
        print "Definition unsupported"    # But you can support it yourself!
        return img

    # Rotate img.
    r = cv2.getRotationMatrix2D(center, float(angle), 1.0)
    dst = cv2.warpAffine(img, r, (1280, 960))

    return dst


def getAngle(vectors):
    "Get the angle from horizontal of the square around the weekday"
    global oldAngle
    directions = []

    # Get vectors coordinates instead of points coordinates.
    for x1,y1,x2,y2 in vectors[0]:
        y = y2-y1
        x = x2-x1

        angle = np.arctan2(y, x)*360/(2*np.pi)

        if angle > 50:
            angle -= 90
        elif angle < -50:
            angle += 90

        if (angle < 45 or angle > -45):
            directions.append(angle)

    # Average computation.
    angleSum = 0
    average = 0
    for angle in xrange(0,len(directions)):
        angleSum += directions[angle]
        average = angleSum/len(directions)

    oldAngle = average

    return average


def maestroReading():
    "Launch Maestro calendar reading, 2nd trial in Nao Challenge 2014"
    try:
        while True:
            # Get the image.
            img = camProxy.getImageRemote(readCalendarCam)
            camProxy.releaseImage(readCalendarCam)

            # Read parameters.
            width    = img[0]
            height   = img[1]
            channels = img[2]
            imgsrc   = img[6]

            # « magical » conversion to OpenCV.
            img = np.fromstring(imgsrc, dtype="uint8").reshape(height,
                                                             width,
                                                             channels)

            # Conversions for color (red) detection.
            hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Red detection.
            lower_red = np.array([ 0, 135, 135])
            upper_red = np.array([5, 255, 255])
            red = cv2.inRange(hsv_img, lower_red, upper_red)
            # Filter red on original.
            newImg = cv2.bitwise_and(img, img, mask=red)

            retval, newImg = cv2.threshold(newImg, 0, 1000, cv2.THRESH_BINARY)

            houghImg = cv2.cvtColor(newImg, cv2.COLOR_BGR2GRAY)
            houghImg = cv2.Canny(houghImg, 50, 250, apertureSize = 7)
            houghImg = cv2.GaussianBlur(houghImg, (5, 5), 5)
            lines = cv2.HoughLinesP(houghImg, 1, np.pi/180, 10,
                                   minLineLength=30,
                                   maxLineGap=5)

            try:
                if lines.any():
                    angle = getAngle(lines)
                    newImg = rotate(newImg, angle)
            except AttributeError:
                global oldAngle
                newImg = rotate(newImg, oldAngle)
                print "No square detected for rotation correction"

            cv2.imwrite("/tmp/imgOCR.tiff", newImg)

            subprocess.call("/home/nao/naoqi/ocr.sh")

            time.sleep(1)

            # Read result of Tesseract treatment.
            file = open('/home/nao/naoqi/output.txt', 'r')
            toSay = file.readline()
            print "Nao reads:",
            print toSay
            toSay = verification(toSay)

            if toSay is not False:
                print "Nao say:",
                print toSay
                try:
                    TTSProxy.say(toSay)
                    return toSay
                except RuntimeError, e:
                    print e
            else:
                print "Nao can't understand weekday"

    except KeyboardInterrupt:
            camProxy.unsubscribe("CalendarCam")


if __name__ == "__main__":
    exit (maestroReading())
