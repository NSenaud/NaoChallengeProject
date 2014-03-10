Caution: this a development version.

# Description

The NaoChallengeGeoloc module have been written for the 2014's Nao Challenge. It allows Nao to guide itself in challenge's room.

---

# Use of the module

## Python

```python
# Create a proxy to the module
NCProxy = ALProxy('NaoChallengeModule', '127.0.0.1', 9559)

# Register our module to the Video Input Module.
NCProxy.registerToVideoDevice(1, 13)

# Get line direction
direction = NCProxy.getDirection()	# Not available currently

# Save image in remote mode.
NCProxy.saveImageRemote('/home/nao/img', 'jpg')

# Unregister.
NCProxy.unRegisterFromVideoDevice()
```