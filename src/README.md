# Description

The NaoChallengeGeoloc module have been written for the 2014's Nao Challenge. It
allows Nao to guide itself in trial's room. It uses a white line which guideNao
accross the room, and [datamatrixes](http://en.wikipedia.org/wiki/Data_Matrix)
on walls to allow Nao to know where he is in the room. Configuration files are
in `~/naoqi/`.


# Requirements

You need qibuild tools from Aldebaran to compile this module. When configured
(look at the doc on Aldebaran's website) you just need to run

``` bash
$ qibuild make
```


# Follow the Line

Here is a sample script to make Nao follow the line in a loop in 2014's room of
Nao Challenge:

``` python
from naoqi import ALProxy
import vision_definitions
import time


IP="NaoCRIC.local"
PORT=9559

def main():
    print 'START TESTING NaoChallengeGeoloc MODULE'

    try:
        print "Creating NaoChallengeGeoloc proxy to ", IP
        NCProxy = ALProxy("NaoChallengeGeoloc",IP,PORT)

    except Exception,e:
        print "Error when creating NaoChallengeGeoloc proxy:"
        print str(e)
        return(1)

    try:
        print "Creating ALMotion proxy to ", IP
        AMProxy = ALProxy("ALMotion",IP,PORT)

    except Exception,e:
        print "Error when creating ALMotion proxy:"
        print str(e)
        return(2)

    try:
        print "Registering to ALVideoDevice"
        NCProxy.registerToVideoDevice(vision_definitions.kVGA,
                                      vision_definitions.kBGRColorSpace)

        # print "Walk from" + str(fromDmtx) + "to" + str(toDmtx)
        NCProxy.walkFromDmtxToDmtx(270, 220)

        try:
            while True:
                print "Turn around"
                AMProxy.moveTo(0, 0, (180*3.14/180))

                print "Walk from 220 to 280"
                NCProxy.walkFromDmtxToDmtx(220, 280)

                print "Turn around"
                AMProxy.moveTo(0, 0, (180*3.14/180))

                print "Walk from 280 to 220"
                NCProxy.walkFromDmtxToDmtx(280, 220)

        except KeyboardInterrupt:
            NCProxy.unRegisterFromVideoDevice()

        print "unRegister from ALVideoDevice"
        NCProxy.unRegisterFromVideoDevice()

    except KeyboardInterrupt:
        NCProxy.unRegisterFromVideoDevice()

    except Exception,e:
        print "NaoChallengeGeoloc test Failed:"
        print str(e)
        print "unRegister from ALVideoDevice"
        NCProxy.unRegisterFromVideoDevice()
        return(3)

if __name__ == "__main__":
  exit (main()) 
```