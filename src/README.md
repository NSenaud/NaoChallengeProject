# Description

The NaoChallengeGeoloc module have been written for the 2014's Nao Challenge. It allows Nao to guide itself in challenge's room. It uses a white line which guide Nao accross the room, and [datamatrixes](http://en.wikipedia.org/wiki/Data_Matrix) on walls to allow Nao to know where he is in the room.


# Use of the module

## Python

```python
from naoqi import ALProxy
import vision_definitions

IP="NomNao.local"
PORT=9559

# Create a proxy to the module
try:
    print "Creating NaoChallengeGeoloc proxy to ", IP
    NCProxy = ALProxy("NaoChallengeGeoloc",IP,PORT)

except Exception,e:
    print "Error when creating NaoChallengeGeoloc proxy:"
    print str(e)
    return(1)

try:
	# Register our module to the Video Input Module.
	print "Registering to ALVideoDevice"
	NCProxy.registerToVideoDevice(vision_definitions.kVGA,
	                              vision_definitions.kBGRColorSpace)

	# Go from Datamatrix 270 to Datamatrix 220 for example.
	print "Walk from 270 to 220"
	NCProxy.walkFromDmtxToDmtx(270, 220)

	# Unregister.
	NCProxy.unRegisterFromVideoDevice()

except KeyboardInterrupt:
    NCProxy.unRegisterFromVideoDevice()

except Exception,e:
    print "NaoChallengeGeoloc test Failed:"
    print str(e)
    return(3)
```