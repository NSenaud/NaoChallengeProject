/**************************************************************************** *
* *                  Nao Challenge 2014 Location Library                    * *
* *************************************************************************** *
* * File: NaoChallengeGeoloc.cpp                                            * *
* *************************************************************************** *
* * Creation:   2014-02-27                                                  * *
* *                                                                         * *
* * Team:       IUT de Cachan                                               * *
* *                                                                         * *
* * Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   * *
* *                                                                         * *
* ****************************************************************************/


/* Project headers */
#include "NaoChallengeGeoloc.h"

/* Standard headers */
#include <iostream>
#include <array>
#include <math.h>
#include <pthread.h>
#include <string>
#include <time.h>
#include <unistd.h>
#include <vector>
/* Boost's headers */
#include <boost/shared_ptr.hpp>
/* OpenCV's headers */
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
/* Aldebaran's headers */
#include <alcommon/albroker.h>
#include <alcommon/almodule.h>
#include <alcommon/alproxy.h>
#include <alproxies/alledsproxy.h>
#include <alproxies/almemoryproxy.h>
#include <alproxies/altexttospeechproxy.h>
#include <alproxies/alvideodeviceproxy.h>
#include <alvision/alvisiondefinitions.h>
#include <alvision/alimage.h>
// #include <consoleloghandler.hpp>
#include <qi/log.hpp>
#include <qi/os.hpp>
/* Lua's headers */
#include <lua.hpp>
#include <lualib.h>
#include <lauxlib.h>


/* Minimum size of the line no Nao's camera 1 */
#define MINLINELENGTH 15


using namespace std;

namespace AL
{
NaoChallengeGeoloc::NaoChallengeGeoloc(boost::shared_ptr<ALBroker> broker,
                                       const std::string& name):
    ALModule(broker, name),
    fRegisteredToVideoDevice(false),
    ImgSrc(cv::Mat())
{
    // Describe the module here. This will appear on the webpage
    setModuleDescription("The 2014's Nao Challege edition geolocalisation module");
    // Define the module example.
    addModuleExample( "Python",
                      "  # Create a proxy to the module \n"
                      "  NCProxy = ALProxy('NaoChallengeModule', '127.0.0.1', 9559)\n\n"
                      "  # Register our module to the Video Input Module. \n"
                      "  NCProxy.registerToVideoDevice(1, 13)\n\n"
                      "  # Go to datamatrix 220 from datamatrix 270. \n"
                      "  NCProxy.walkFromDmtxToDmtx(270, 220)\n\n"
                      "  # Unregister.\n"
                      "  NCProxy.unRegisterFromVideoDevice()\n");

    /**
    * Define callable methods with their descriptions:
    * This makes the method available to other cpp modules
    * and to python.
    * The name given will be the one visible from outside the module.
    * This method has no parameters or return value to describe
    * functionName(<method_name>, <class_name>, <method_description>);
    * BIND_METHOD(<method_reference>);
    */
    functionName("sayText",
                 getName(),
                 "Say a given sentence.");
    /**
    * addParam(<attribut_name>, <attribut_descrption>);
    * This enables to document the parameters of the method.
    * It is not compulsory to write this line.
    */
    addParam("toSay", "The sentence to be said.");
    BIND_METHOD(NaoChallengeGeoloc::sayText);

    /**
     * registerToVIM : Register to the V.I.M.
     */
    functionName("registerToVideoDevice",
                 getName(),
                 "Register to the V.I.M." );
    addParam("resolution", "Resolution requested.");
    addParam("colorSpace", "Colorspace requested.");
    BIND_METHOD(NaoChallengeGeoloc::registerToVideoDevice);

    /**
     * unRegisterFromVIM : Unregister from the V.I.M.
     */
    functionName("unRegisterFromVideoDevice",
                 getName(),
                 "Unregister from the V.I.M." );
    BIND_METHOD(NaoChallengeGeoloc::unRegisterFromVideoDevice);


    functionName("onDatamatrixDetection",
                 getName(),
                 "run onDatamatrixDetection" );
    BIND_METHOD(NaoChallengeGeoloc::onDatamatrixDetection);

    /**
    * Walk.
    */
    functionName("walkFromDmtxToDmtx",
                 getName(),
                 "Go from a datamatrix to another datamatrix.");
    addParam("fromDatamatrix", "Number of Datamatrix Nao is starting from");
    addParam("toDatamatrix", "Number of Datamatrix Nao is going from");
    BIND_METHOD(NaoChallengeGeoloc::walkFromDmtxToDmtx);

    functionName("stopWalk",
                 getName(),
                 "Stop walking (if walkFromDmtxToDmtx() was called with post).");
    BIND_METHOD(NaoChallengeGeoloc::stopWalk);

    // We create proxies
    speechProxy = getParentBroker()->getProxy("ALTextToSpeech");
    moveProxy = getParentBroker()->getProxy("ALMotion");
    postureProxy = getParentBroker()->getProxy("ALRobotPosture");
    ledsProxy = getParentBroker()->getProxy("ALLeds");
}


void NaoChallengeGeoloc::exit()
{
  AL::ALModule::exit();
}


NaoChallengeGeoloc::~NaoChallengeGeoloc()
{
    // Unregister the video module.
    try
    {
        if(fCamProxy) fCamProxy->unsubscribe(fVideoClientName);

        fCamProxy.reset();
    }
    catch(const AL::ALError& e)
    {
        qiLogError("vision.NaoChallengeGeoloc") <<  e.toString() << std::endl;
    }
}


void NaoChallengeGeoloc::init()
{
    // Create a proxy to the ALVideoDevice.
    try {
        fCamProxy = boost::shared_ptr<ALVideoDeviceProxy>(new ALVideoDeviceProxy(getParentBroker()));
    }
    catch (const AL::ALError& e) {
        qiLogError("vision.NaoChallengeGeoloc")
            << "Error while getting proxy on ALVideoDevice.  Error msg "
            << e.toString() << std::endl;
        NaoChallengeGeoloc::exit();
        return;
    }

    // Create a proxy to the ALMemory.
    try {
        fMemoryProxy = boost::shared_ptr<ALMemoryProxy>(new ALMemoryProxy(getParentBroker()));
    }
    catch (const AL::ALError& e) {
        qiLogError("memory.NaoChallengeGeoloc")
            << "Error while getting proxy on ALMemory.  Error msg "
            << e.toString() << std::endl;
        NaoChallengeGeoloc::exit();
        return;
    }

    if(fCamProxy == NULL)
    {
        qiLogError("vision.NaoChallengeGeoloc")
            << "Error while getting proxy on ALVideoDevice. Check ALVideoDevice is running."
            << std::endl;
        NaoChallengeGeoloc::exit();
        return;
    }

    qiLogInfo("vision.NaoChallengeGeoloc")
        << "Use registerToVideoDevice + "
           "saveImageLocal + unRegisterFromVideoDevice to save images."
        << std::endl;
}


/**
 * registerToVIM
 */
void NaoChallengeGeoloc::registerToVideoDevice(const int &pResolution,
                                               const int &pColorSpace)
{
    // If we've already registered a module, we need to unregister it first !
    if (fRegisteredToVideoDevice)
    {
        throw ALError(getName(),
                      "registerToVideoDevice()",
                      "A video module has already been "
                      "registered. Call unRegisterFromVideoDevice() before trying to register a new module.");
    }

    // GVM Name that we're going to use to register.
    const std::string kOriginalName = "NaoChallengeGeoloc";
    int imgWidth = 0;
    int imgHeight = 0;
    int imgNbLayers = 0;
    const int kImgDepth = 8;
    const int kFps = 5;

    // Release Image Header if it has been allocated before.
    if (!ImgSrc.empty()) ImgSrc.release();

    setSizeFromResolution(pResolution, imgWidth, imgHeight);
    imgNbLayers = getNumLayersInColorSpace(pColorSpace);

    if (imgWidth == -1 || imgWidth == -1 || imgNbLayers == -1)
    {
        throw ALError(getName(),
                      "registerToVideoDevice()",
                      "Invalid resolution or color space.");
    }

    // Allocate our Image header.
    int type;
    type = (imgNbLayers) == 3 ? CV_8UC3 : CV_8UC1;
    ImgSrc = cv::Mat(cv::Size(imgWidth, imgHeight), type);

    if (ImgSrc.empty())
    {
        throw ALError(getName(),
                      "registerToVideoDevice()",
                      "Fail to allocate OpenCv image header.");
    }

    // Call the "subscribe" function with the given parameters.
    if(fCamProxy)
        fVideoClientName = fCamProxy->subscribeCamera(kOriginalName,
                                                      1,
                                                      pResolution,
                                                      pColorSpace,
                                                      kFps);

    qiLogInfo("vision.NaoChallengeGeoloc")
        << "Module registered as " << fVideoClientName << std::endl;

    // Registration is successful, set fRegisteredToVim to true.
    fRegisteredToVideoDevice = true;
}


/**
 * unRegisterFromVIM
 */
void NaoChallengeGeoloc::unRegisterFromVideoDevice()
{
    if (!fRegisteredToVideoDevice)
    {
        throw ALError(getName(),
                      "unRegisterFromVideoDevice()",
                      "No video module is currently "
                      "registered! Call registerToVideoDevice first.");
    }

    // Release Image Header if it has been allocated.
    if (!ImgSrc.empty()) ImgSrc.release();

    qiLogInfo("vision.NaoChallengeGeoloc")
        << "try to unregister " << fVideoClientName << " module." << std::endl;

    if(fCamProxy) fCamProxy->unsubscribe(fVideoClientName);

    qiLogInfo("vision.NaoChallengeGeoloc")
        << "Done." << std::endl;

    // UnRegistration is successful, set fRegisteredToVim to false.
    fRegisteredToVideoDevice = false;
}


void NaoChallengeGeoloc::sayText(const std::string &toSay)
{
    std::cout << "Saying the phrase in the console..." << std::endl;
    std::cout << toSay << std::endl;

    speechProxy->callVoid("setVolume", 0.55f);

    try
    {
        speechProxy->pCall("say", toSay);
    }

    catch (const AL::ALError&)
    {
        qiLogError("module.NaoChallengeGeoloc")
            << "Could not get proxy to ALTextToSpeech" << std::endl;
    }
}


void NaoChallengeGeoloc::stopWalk()
{
    moveProxy->callVoid("stopMove");
}


void NaoChallengeGeoloc::onDatamatrixDetection(const std::string &key,
                                               const AL::ALValue &value,
                                               const AL::ALValue &message)
{
    // Update the global variable to signal datamatrix detection to
    // walkFromDmtxToDmtx() function.
    Datamatrix = value;
}


// Main function
void NaoChallengeGeoloc::walkFromDmtxToDmtx(const int &fromDatamatrix,
                                            const int &toDatamatrix)
{
    bool succeed;                   // Is a line detected?
    cv::vector<cv::Vec4i> lines;    // Line's vectors position.
    long long timeStamp;            // Timestamp of analysed picture.
    float averageX;                 // Relative line's position.
    float oldAverageX = 0;          // Relative line's position at last loop.
    float averageAngle;             // Line's direction (in degres).
    float oldAverageAngle = 0.f;    // Line's direction at last loop.
    float consigne;                 // Direction (in Radians)
    float oldConsigne = 0;          // Direction gave at last loop.
    int fail = 0;                   // Number of loop without line detection.
    float distance = 0.0;           // Distance walked.
    time_t now;
    AL::ALValue articulation = "HeadYaw";

    if(fMemoryProxy) // ALMemory proxy to get detected datamatrix value
    {
        fMemoryProxy->subscribeToEvent("DatamatrixDetection",
                                       "NaoChallengeGeoloc",
                                       "onDatamatrixDetection");
    }

    qiLogInfo("vision.NaoChallengeGeoloc")
        << "Module registered as " << fVideoClientName << std::endl;

    qiLogInfo("NaoChallengeGeoloc")
        << "Start from " << fromDatamatrix << endl;

    qiLogInfo("NaoChallengeGeoloc")
        << "<-- Loading Configuration -->" << endl;

    /* Getting first movments from a lua config file */
    const char* configFile = "/home/nao/naoqi/NaoChallenge/config.lua";
    const char* configFunc = "getConfigFromDmtx";
    const char* endConfigFunc = "distanceDependingOnDmtx";
    const char* correctionConfigFunc = "getConfigForCorrectionModule";

    lua_State* L = luaL_newstate();

    // Get start config depending on starting Datamatrix.
    float startAngle = 0;
    float startXDist = 0;
    float startYDist = 0;
    // Get param depending on destination.
    float distanceMax = 0;
    float endAngle = 0;
    float endXDist = 0;
    float endYDist = 0;
    // Get correction module configuration.
    int   lineHysteresisLevel     = 0;
    float angleIfBeyondHysteresis = 0;
    float footstep                = 0;
    int   waitBetweenSteps        = 0;

    luaL_openlibs(L);

    if (luaL_dofile(L, configFile) != 0) // Load file.
    {
        qiLogInfo("Error while loading lua config file")
            << configFile
            << lua_tostring(L, -1) << std::endl;
    }
    else
    {
        // Get start config depending on starting Datamatrix.
        lua_getglobal(L, configFunc); // Function to call.
        lua_pushnumber(L, fromDatamatrix); // Argument.
        if (lua_pcall(L, 1, 3, 0) != 0) // Run function with 1 arg & 1 return.
        {
            // const char* luaError = lua_tostring(L, -1));
            qiLogInfo("Error while running function in lua config file")
                << configFunc
                << lua_tostring(L, -1) << std::endl;
        }
        else
        {
            startAngle = (float) lua_tonumber(L, -3);
            startXDist = (float) lua_tonumber(L, -2);
            startYDist = (float) lua_tonumber(L, -1);
            lua_pop(L, 3); // clear the stack.
        }

        // Get param depending on destination.
        lua_getglobal(L, endConfigFunc); // Function to call.
        lua_pushnumber(L, toDatamatrix); // Argument.
        if (lua_pcall(L, 1, 4, 0) != 0) // Run function with 1 arg & 1 return.
        {
            // const char* luaError = lua_tostring(L, -1));
            qiLogInfo("Error while running function in lua config file")
                << endConfigFunc
                << lua_tostring(L, -1) << std::endl;
        }
        else
        {
            distanceMax = (float) lua_tonumber(L, -4);
            endAngle = (float) lua_tonumber(L, -3);
            endXDist = (float) lua_tonumber(L, -2);
            endYDist = (float) lua_tonumber(L, -1);
            lua_pop(L, 4); // clear the stack.
        }

        // Get correction module configuration.
        lua_getglobal(L, correctionConfigFunc); // Function to call.
        if (lua_pcall(L, 0, 4, 0) != 0) // Run function with 1 arg & 1 return.
        {
            // const char* luaError = lua_tostring(L, -1));
            qiLogInfo("Error while running function in lua config file")
                << configFunc
                << lua_tostring(L, -1) << std::endl;
        }
        else
        {
            lineHysteresisLevel     = (int)   lua_tonumber(L, -4);
            angleIfBeyondHysteresis = (float) lua_tonumber(L, -3);
            footstep                = (float) lua_tonumber(L, -2);
            waitBetweenSteps        = (int)   lua_tonumber(L, -1);
            lua_pop(L, 4); // clear the stack.
        }
    }

    lua_close(L);

    // Block the right arm when Nao keep the key in it hand.
    if (toDatamatrix == 290) moveProxy->pCall("setWalkArmsEnabled",
                                            true,
                                            false);

    // Position Nao on te line depending on it position in the room.
    // postureProxy->callVoid("goToPosture",
    //                        (std::string) "StandInit",
    //                        1.0f);

    consigne = startAngle * CV_PI/180;    // Conversion in radians.
    moveProxy->pCall("moveTo",
                     (float) startXDist,
                     (float) startYDist,
                     (float) consigne);

    qiLogInfo("NaoChallengeGeoloc")
        << "Angle (Radian): " << consigne << endl;

    usleep(1000*8000);

    /* *** Main loop *** */
    while(true)
    {
        qiLogInfo("NaoChallengeGeoloc")
            << "------------ [ NEW LOOP ITERATION ] ------------" << endl;

        qiLogInfo("NaoChallengeGeoloc")
            << "toDatamatrix = " << toDatamatrix
            << "\nDatamatrix = " << (std::string) Datamatrix
            << endl;

        qiLogInfo("NaoChallengeGeoloc")
            << "Distance = " << distance
            << "\nDistance max = " << distanceMax
            << endl;

        // Reach Datamatrix !
        std::string DatamatrixString = (std::string) Datamatrix ;
        ostringstream toDatamatrixString;
        toDatamatrixString << toDatamatrix ;
        if ((DatamatrixString == toDatamatrixString.str()
          && distanceMax != 0
          && distanceMax < distance)
         || (DatamatrixString == toDatamatrixString.str()
          && distanceMax == 0))
        {
            ledsProxy->pCall("rasta",
                             (float) 8.0f);
            break;
        }
        // Reach destination
        if (distanceMax != 0 && distanceMax < distance)
        {
            consigne = endAngle * CV_PI/180;
            moveProxy->pCall("moveTo",
                             (float) endXDist,
                             (float) endYDist,
                             (float) consigne);
            break;
        }

        // Analyse a new picture with OpenCV to find the line.
        findLine(succeed, lines, timeStamp);

        // Succeed if any line is detected on the picture.
        if (succeed)
        {
            // Find informations on line detected.
            directionFromVectors(lines, averageX, averageAngle);

            /* ********************* Correction Module ********************* */

            // Correction of the angle, set 12 o'clock at 0.
            averageAngle -= 90;
            averageAngle = -averageAngle;
            // Set center to 0 to have relative place in vision.
            averageX -= 320;

            qiLogInfo("NaoChallengeGeoloc")
                << "Angle (before correction): " << averageAngle << endl;

            qiLogInfo("NaoChallengeGeoloc")
                << "Line's relative position (in pixel): " << averageX << endl;

            if (averageX > lineHysteresisLevel)
            {
                qiLogInfo("NaoChallengeGeoloc")
                    << "Nao is on the LEFT of the line" << endl;
                qiLogInfo("NaoChallengeGeoloc")
                        << "/!\\ Nao is loosing the line!" << endl;

                averageAngle = -angleIfBeyondHysteresis;
            }
            else if (averageX < -lineHysteresisLevel)
            {
                qiLogInfo("NaoChallengeGeoloc")
                    << "Nao is on the RIGHT of the line" << endl;
                qiLogInfo("NaoChallengeGeoloc")
                        << "/!\\ Nao is loosing the line!" << endl;
                averageAngle = angleIfBeyondHysteresis;
            }
            else
            {
                qiLogInfo("NaoChallengeGeoloc")
                    << "Nao is on the line" << endl;

                averageAngle = (averageAngle + oldAverageAngle)/2;
            }

            oldAverageX     = averageX;
            oldAverageAngle = averageAngle;

            // Radian Conversion.
            consigne = averageAngle * CV_PI/180;

            //!\ Security
            if (consigne < -2.5)
            {
                consigne = -2.5;
            }
            else if (consigne > 2.5)
            {
                consigne = 2.5;
            }
            else if (!(consigne > -2.5 && consigne < 2.5))
            {
                consigne = -oldConsigne;
            }

            qiLogInfo("NaoChallengeGeoloc")
                << "Consigne (Degres): " << averageAngle << endl;
            qiLogInfo("NaoChallengeGeoloc")
                << "Consigne (Radian): " << consigne << endl;

            // Rotate head.
            moveProxy->pCall("angleInterpolation",
                             articulation,
                             (AL::ALValue) consigne,
                             (AL::ALValue) 0.1f,
                             (bool) true);

            moveProxy->pCall("moveTo",
                             (float) footstep,
                             (float) 0.0f,
                             (float) consigne);

            ledsProxy->pCall("earLedsSetAngle",
                             (int)   averageAngle,
                             (float) 0.5f,
                             (bool)  false);
            distance += footstep;

            oldConsigne = consigne;

            usleep(1000 * waitBetweenSteps);   // 1000 * ms.
        }
        else
        {
            ++fail;
            // Turns head (probably) back to the line.
            moveProxy->pCall("angleInterpolation",
                             articulation,
                             (AL::ALValue) -consigne,
                             (AL::ALValue) 0.5f,
                             (bool) true);
        }
    }

    Unsubscribe Video
    try
    {
        if(fCamProxy) fCamProxy->unsubscribe(fVideoClientName);

        fCamProxy.reset();
    }
    catch(const AL::ALError& e)
    {
        qiLogError("vision.NaoChallengeGeoloc") <<  e.toString() << std::endl;
    }
}


void NaoChallengeGeoloc::findLine(bool &succeed,
                                  cv::vector<cv::Vec4i> &lines,
                                  long long &timeStamp)
{
    cv::Mat dst, color_dst, hsv, whiteFilter ;

    // Check a video module has been registered.
    if (!fRegisteredToVideoDevice)
    {
        throw ALError(getName(),
                      "findLine()",
                      "No video module is currently "
                      "registered! Call registerToVideoDevice() first.");
    }

    ALImage* imageIn = NULL;

    // Now you can get the pointer to the video structure.
    imageIn = (ALImage*)fCamProxy->getImageLocal(fVideoClientName);
    if (!imageIn)
    {
        throw ALError(getName(), "findLine", "Invalid image returned.");
    }

    timeStamp = imageIn->getTimeStamp();
    const int seconds = (int)(timeStamp/1000000LL);

    ImgSrc.data = imageIn->getData();;

    // Conversion from BGR colorspace to HSV colorspace:
    cv::cvtColor(ImgSrc, hsv, cv::COLOR_BGR2HSV);

    // Definition of white:
    cv::inRange(hsv, cv::Scalar(0, 0, 240),
                     cv::Scalar(255, 255, 255), whiteFilter);

    // Filtering white:
    cv::bitwise_and(ImgSrc, ImgSrc, dst, whiteFilter);

    // Conversion for lines detection:
    cv::cvtColor(dst, color_dst, cv::COLOR_HSV2BGR);
    cv::cvtColor(color_dst, dst, cv::COLOR_BGR2GRAY);
    cv::Canny(dst, dst, 30, 180, 3);

    // Lines detection:
    cv::HoughLinesP(dst, lines, 1, CV_PI/180.,100, MINLINELENGTH, 5);

    for (size_t i = 0 ; i < lines.size() ; i++)
    {
        cv::line(color_dst, cv::Point(lines[i][0], lines[i][1]),
                            cv::Point(lines[i][2], lines[i][3]),
                            cv::Scalar(0, 0, 255), 3, 8);
    }

    ImgSrc = color_dst;
    xSaveIplImage(color_dst, "/tmp/imgFromCam", "jpg", seconds);

    fCamProxy->releaseImage(fVideoClientName);

    if (!lines.empty())
    {
        succeed = true;
    }
    else
    {
        succeed = false;
    }
}


void NaoChallengeGeoloc::directionFromVectors(cv::vector<cv::Vec4i> &lines,
                                              float &averageX,
                                              float &averageAngle)
{
    std::vector<float> vectors;
    int sumX = 0;
    int x;
    int y;

    for (int i = 0; i < lines.size(); ++i)
    {
        if (lines[i][3] > 300 || lines[i][1] > 300)
        {
            y = lines[i][3]-lines[i][1];
            x = lines[i][2]-lines[i][0];

            vectors.push_back( (float) atan2(y ,x)*360/(2*CV_PI));

            sumX += lines[i][2];
            sumX += lines[i][0];
        }
    }

    if (vectors.size() == 0)
    {
        qiLogInfo("NaoChallengeGeoloc")
            << "!!!!!!!!!!!!!!!!!! [ CAUTION ] !!!!!!!!!!!!!!!!!" << endl;
        for (int i = 0; i < lines.size(); ++i)
        {
            y = lines[i][3]-lines[i][1];
            x = lines[i][2]-lines[i][0];

            vectors.push_back( (float) atan2(y ,x)*360/(2*CV_PI));

            sumX += lines[i][2];
            sumX += lines[i][0];
        }
    }

    // Average positon of the line.
    averageX = sumX/(2*vectors.size());

    float angleSum = 0;
    for (int i = 0; i < vectors.size(); ++i)
    {
        // Correction of a positive/negative degres problem.
        if (vectors[i] < 0)
        {
            vectors[i] = 180 + vectors[i];
        }

        // Keep safe from horizontal lines...
        if (vectors[i] > 150 || vectors[i] < 30)
        {
            vectors.erase(vectors.begin() + i);
            i -= 1;
        }
        else
        {
            angleSum += vectors[i];
        }
    }

    averageAngle = angleSum/vectors.size();
}


// Actually perform the cvSaveImage operation.
void NaoChallengeGeoloc::xSaveIplImage(const cv::Mat &img,
                                       const std::string& pName,
                                       const std::string& pImageFormat,
                                       int seconds)
{
    std::stringstream ss;
    ss << pName << seconds << "." << pImageFormat;
    const std::string kImageNameFull = ss.str();

    try {
        cv::imwrite(kImageNameFull, ImgSrc);
        qiLogInfo("vision.genericvideomodule") << "Image saved as " << kImageNameFull << std::endl;
    }
    catch(const cv::Exception& e) {
        qiLogError("vision.genericvideomodule") << "OpenCV can't save the image "
                                                << "with this format. (e.g. "
                                                << "incompatible file format"
                                                << " / no space left)  Error msg "
                                                << e.err << std::endl;
    }
}
} // namespace AL
