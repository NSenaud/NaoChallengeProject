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

import sys
import time
import numpy as np                  # Numpy:  Maths library.
import cv2                          # OpenCV: Visual recognition library.
import vision_definitions           # Image definitions macros.
import subprocess

# Nao's libraries.
from naoqi import ALProxy


IP = "NaoCRIC.local"
Port = 9559
weekdays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


camProxy = ALProxy("ALVideoDevice", IP, Port)
TTSProxy = ALProxy("ALTextToSpeech", IP, Port)

# Register a video module.
colorSpace = vision_definitions.kBGRColorSpace
definition = vision_definitions.k4VGA
fps = 5
camera = 0      # 1 = mouth camera / 0 = front camera.

followTheLineCam = camProxy.subscribeCamera("CalendarCam",
                                            camera,
                                            definition,
                                            colorSpace,
                                            fps)

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
    "Find the clothest weekday from proposition"
    
    global weekdays
    bestDay = [None, 1000]  # [ Day, matchCoeff ]

    for day in weekdays:
        match = levenshtein(day, proposition)
        if match == 1:
            return day
        elif match < bestDay[1]:
            bestDay[0] = day
            bestDay[1] = match

    if bestDay[1] < 7:
        return bestDay[0]
    else:
        return ""

try:
    while True:
        # Get the image.
        img = camProxy.getImageRemote(followTheLineCam)
        camProxy.releaseImage(followTheLineCam)

        # Read parameters.
        width = img[0]
        height = img[1]
        channels = img[2]
        imgsrc = img[6]

        # « magical » conversion to OpenCV.
        img = np.fromstring(imgsrc, dtype="uint8").reshape(height,
                                                           width,
                                                           channels)

        # Conversions for color (red) detection.
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Red detection.
        lower_red = np.array([ 0, 135, 135])
        upper_red = np.array([10, 255, 255])
        red = cv2.inRange(hsv_img, lower_red, upper_red)
        # Filter red on original.
        img = cv2.bitwise_and(img, img, mask=red)

        retval, img = cv2.threshold(img, 0, 1000, cv2.THRESH_BINARY)

        img = cv2.medianBlur(img, 5)

        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img = cv2.Canny(img, 100, 125)

        # contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # cv2.drawContours(img, contours, -1, 1000)

        cv2.imwrite("/tmp/imgOCR.tiff", img)

        subprocess.call("/home/nao/naoqi/ocr.sh")

        time.sleep(1)

        file = open('/home/nao/naoqi/output.txt', 'r')
        toSay = file.readline()

        if not (toSay.isspace() or toSay == ""):
            print "Nao sees:",
            print toSay
            toSay = verification(toSay)
            print "Nao say:",
            print toSay
            try:
                TTSProxy.say(toSay)
            except RuntimeError, e:
                print e
        else:
            print "Nao can't read"

except KeyboardInterrupt:
        camProxy.unsubscribe("CalendarCam")