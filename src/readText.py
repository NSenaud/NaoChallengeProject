#!/usr/bin/env python
# -*- coding:Utf-8 -*-

# ########################################################################### #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: getCalendarDay.py                                                 # #
# ########################################################################### #
# # Creation:   2014-03-10                                                  # #
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
import subprocess

# Nao's libraries.
from naoqi import ALProxy


IP="NaoCRIC.local"
Port=9559


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

        cv2.imwrite("/tmp/imgOCR.tiff", img)

        subprocess.call("/home/nao/naoqi/ocr.sh")

        time.sleep(1)

        file = open('/home/nao/naoqi/output.txt', 'r')
        toSay = file.readline()
        print "Nao say:",
        print toSay
        try:
            TTSProxy.say(toSay)
        except RuntimeError, e:
            print e

except KeyboardInterrupt:
        camProxy.unsubscribe("CalendarCam")