cmake_minimum_required(VERSION 2.8)

# Give a name to the project.
project(NaoChallengeGeoloc)

# You need this to find the qiBuild CMake framework
find_package(qibuild)


# Create a list of source files
set(_srcs
    NaoChallengeGeoloc.cpp
    NaoChallengeGeoloc.h
    main.cpp)


# Create a plugin, that is a shared library, and make
# sure it is built in lib/naoqi
qi_create_lib(NaoChallengeGeoloc SHARED ${_srcs} SUBFOLDER naoqi)

# Tell CMake that myproject depends on ALCOMMON.
# This will set the libraries to link myproject with,
# the include paths, and so on
qi_use_lib(NaoChallengeGeoloc ALCOMMON ALVISION BOOST OPENCV2_CORE OPENCV2_HIGHGUI OPENCV2_IMGPROC)








