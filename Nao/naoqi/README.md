# Description

Those files must be installed on `~/naoqi/` folder on Nao.


# Use of the module

If you wish to use the module, look at `launchLibNaoChallengeExample.py` to know
how to.


## Configuration

The file `config.lua` is used to configure how Nao should react depending on the
starting and finishing datamatrixies. The file is read at each start of the
module, so you can modify it at anytime and modifications will take effect on
next call to localisation module. No restart of the robot is required.


# Trials

## Nao Memento

For this trial Python code is used to get the key. Localisation module is called
before (to reach the key) and after (to put away the key).


## Nao Maestro

For this trial, in addition to localisation module, we use a Python script to
guide the trial, in association with bash. When Nao reach the calendar, it
begins an OpenCV treatment te keep red, then rotate the picture to keep it
horizontal. Then it saves the picture in `/tmp/` and launch a Bash script to
launch Tesseract OCR software. Finally, the Python script read a text file in
`/tmp/` wrote by Tesseract.


## Nao Gato

For Nao Gato, we still use the localisation module, and in add we use a Lua
script to launch the Bluetooth connexion.
```
