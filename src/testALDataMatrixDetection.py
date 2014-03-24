
# -*- coding: utf-8 -*-
"""
    Simple python script to test ALDataMatrixDetection
"""

from naoqi import ALProxy
import time


IP="NaoCRIC.local"
PORT=9559


def main():
    print 'START TESTING ALDataMatrixDetection MODULE'

    try:
        print "Creating ALDataMatrixDetection proxy to ", IP
        DDProxy = ALProxy("ALDataMatrixDetection",IP,PORT)

    except Exception,e:
        print "Error when creating ALDataMatrixDetection proxy:"
        print str(e)
        return(1)

    try:
	print "Creating ALTextToSpeech proxy to ", IP       
        tts = ALProxy("ALTextToSpeech", IP, PORT)
    except Exception,e:
        print "Error when creating ALTextToSpeech proxy:"
        print str(e)
        return(1)

    try:
        print "Version of ALDataMatrixDetection is",
        print DDProxy.version()

	print "Set Debug Mode on True"
	DDProxy.setDebugMode(True)

	print "Set resolution to VGA"
	DDProxy.setResolution(2)

	#print "Set detection timeout to 10 000 milliseconds" 
	#DDProxy.setDetectionTimeOut(10000)
	
	while True:
	    print "Shooting..."
	    DataMatrixDetected = DDProxy.processOneShot(False, [0,0])        
            
	    try:
                DataMatrixValue = str(DataMatrixDetected[7][0][0])[2:5]
	    
            except Exception,e:
                DataMatrixValue = 0

	    print "Datamatrix value:",
	    print DataMatrixValue
	    
	    if (int(DataMatrixValue) > 200 and int(DataMatrixValue) < 300):
	         tts.say(DataMatrixValue)

	    time.sleep(1)

    except KeyboardInterrupt:
	DDProxy.unsubscribeCamera()

    except Exception,e:
	DDProxy.unsubscribeCamera()
        print "ALDataMatrixDetection test Failed:"
        print str(e)
        return(1)

if __name__ == "__main__":
  exit (main()) 