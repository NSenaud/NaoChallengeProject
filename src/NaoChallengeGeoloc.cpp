/**************************************************************************** *
* *                  Nao Challenge 2014 Location Library                    * *
* *************************************************************************** *
* * File: NaoChallengeGeoloc.cpp                                            * *
# *************************************************************************** *
* * Creation:   2014-02-27                                                  * *
* *                                                                         * *
* * Team:       IUT de Cachan                                               * *
* *                                                                         * *
* * Authors:    Nicolas SENAUD                                              * *
* *             Pierre-Guillaume LEGUAY                                     * *
* *             Nicolas SAREMBAUD                                           * *
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
/* Boost headers */
#include <boost/shared_ptr.hpp>
/* OpenCV headers */
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
/* Aldebaran headers */
#include <alcommon/albroker.h>
#include <alcommon/almodule.h>
#include <alcommon/alproxy.h>
#include <alproxies/almemoryproxy.h>
#include <alproxies/altexttospeechproxy.h>
#include <alproxies/alvideodeviceproxy.h>
#include <alvision/alvisiondefinitions.h>
#include <alvision/alimage.h>
// #include <consoleloghandler.hpp>
#include <qi/log.hpp>
#include <qi/os.hpp>


/* Minimum size of the line no Nao's camera 1 */
#define MINLINELENGTH 15

#define _USE_MATH_DEFINES


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

    // Create a proxy to the ALMemoryProxy.
    try {
        fMemoryProxy = boost::shared_ptr<ALMemoryProxy>(new ALMemoryProxy(getParentBroker()));
    }
    catch (const AL::ALError& e) {
        qiLogError("memory.NaoChallengeGeoloc") 
            << "Error while getting proxy on ALMemoryProxy.  Error msg "
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
    const int kFps = 3;

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

    qiLogInfo("vision.NaoChallengeGeoloc") << "Module registered as " << fVideoClientName << std::endl;

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
        << "try to unregister "
        << fVideoClientName
        << " module."
        << std::endl;

    if(fCamProxy) fCamProxy->unsubscribe(fVideoClientName);

    qiLogInfo("vision.NaoChallengeGeoloc")
        << "Done."
        << std::endl;

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
            << "Could not get proxy to ALTextToSpeech"
            << std::endl;
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
    Datamatrix = value;
}


void NaoChallengeGeoloc::walkFromDmtxToDmtx(const int &fromDatamatrix,
                                            const int &toDatamatrix)
{
    bool succeed;
    cv::vector<cv::Vec4i> lines;
    long long timeStamp;
    float averageX;
    float oldAverageX = 320;
    float averageAngle;
    float oldAverageAngle = 0.f;
    float consigne;
    float oldConsigne = 0;
    int fail = 0;

    AL::ALValue articulation = "HeadYaw";

    time_t now;

    if(fMemoryProxy)
    {
        fMemoryProxy->subscribeToEvent("DatamatrixDetection",
                                       "NaoChallengeGeoloc",
                                       "onDatamatrixDetection");
    }

    qiLogInfo("vision.NaoChallengeGeoloc") << "Module registered as " << fVideoClientName << std::endl;

    // moveProxy->callVoid("wakeUp");
    postureProxy->callVoid("goToPosture",
                           (std::string) "StandInit",
                           1.0f);

    std::ostringstream toSay;
    toSay << "Je suis prêt!" ;
    sayText(toSay.str());

    qiLogInfo("NaoChallengeGeoloc")
        << "Start from " << fromDatamatrix << endl;

    switch (fromDatamatrix)
    {
        case 210:   break;

        case 220:   break;

        case 230:   break;

        case 240:   break;

        case 250:   break;

        case 260:   break;

        case 270:   consigne = -45*CV_PI/180;    // 45 degres in radians.
                    moveProxy->pCall("moveTo",
                                     (float)  0.3f,
                                     (float) -0.3f,
                                     (float) consigne);

                    qiLogInfo("NaoChallengeGeoloc")
                        << "Angle (Radian): " << consigne << endl;

                    usleep(1000*4000);
                    
                    break;

        case 280:   break;

        case 290:   break;
    }


    while(fail < 100)
    {
        qiLogInfo("NaoChallengeGeoloc")
            << "------------ [ NEW LOOP ITERATION ] ------------" << endl;
        
        qiLogInfo("NaoChallengeGeoloc")
            << "toDatamatrix = " << toDatamatrix
            << "\nDatamatrix = " << (std::string) Datamatrix
            << endl;

        // Reach Datamatrix !
        std::string DatamatrixString = (std::string) Datamatrix ;
        ostringstream toDatamatrixString;
        toDatamatrixString << toDatamatrix ;
        if (DatamatrixString == toDatamatrixString.str())
        {
            sayText("Datamatrice de destination atteinte");

            break;
        }

        findLine(succeed, lines, timeStamp);

        if (succeed)
        {
            directionFromVectors(lines, averageX, averageAngle);           

            /* ********************* Correction Module ********************* */

            // Correction of the angle, set 12 o'clock at 0.
            averageAngle -= 90;
            averageAngle = -averageAngle;
            // Correction of the place of the line in vision, set center to 0.
            averageX -= 320;


            qiLogInfo("NaoChallengeGeoloc")
                << "Angle (Avant correcteur): " << averageAngle << endl;

            qiLogInfo("NaoChallengeGeoloc")
                << "Position de la ligne (pixel): " << averageX << endl;


            if (averageX > 80)
            {
                qiLogInfo("NaoChallengeGeoloc")
                    << "Nao is on the LEFT of the line" << endl;
                qiLogInfo("NaoChallengeGeoloc")
                        << "/!\\ Nao is loosing the line!" << endl;

                averageAngle = -15;
            }
            else if (averageX < -80)
            {
                qiLogInfo("NaoChallengeGeoloc")
                    << "Nao is on the RIGHT of the line" << endl;
                qiLogInfo("NaoChallengeGeoloc")
                        << "/!\\ Nao is loosing the line!" << endl;
                averageAngle = 15;
            }
            else
            {
                qiLogInfo("NaoChallengeGeoloc")
                    << "Nao is on the line" << endl;

                averageAngle = (averageAngle+oldAverageAngle)/2;
            }

            oldAverageX     = averageX;
            oldAverageAngle = averageAngle;

            
            // Radian Conversion.
            consigne = averageAngle*CV_PI/180;

            // Security
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

            AL::ALValue articulation = "HeadYaw";

            moveProxy->pCall("angleInterpolation",
                             articulation,
                             (AL::ALValue) consigne, // (((float) atan((float) 80*averageX/35200))*CV_PI/180),
                             (AL::ALValue) 0.1f,
                             (bool) true);

            moveProxy->pCall("moveTo",
                             (float) 0.05f,
                             (float) 0.0f,
                             (float) consigne);

            oldConsigne = consigne;

            usleep(1000*500);   // 500 ms.
        }
        else
        {
            ++fail;
            moveProxy->pCall("angleInterpolation",
                             articulation,
                             (AL::ALValue) -consigne,
                             (AL::ALValue) 0.5f,
                             (bool) true);
        }
    }

    postureProxy->callVoid("goToPosture",
                           (std::string) "Crouch",
                           0.5f);

    sayText("Blope blop blop");

    moveProxy->callVoid("setStiffnesses",
                        (AL::ALValue) "Body",
                        (AL::ALValue) 0.0f);
}


void NaoChallengeGeoloc::findLine(bool &succeed,
                                  cv::vector<cv::Vec4i> &lines,
                                  long long &timeStamp)
{
    cv::Mat dst, color_dst, hsv, whiteFilter ;
    
    // Check that a video module has been registered.
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
    cv::inRange(hsv, cv::Scalar(0, 0, 255),
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

    // ImgSrc = color_dst;
    // xSaveIplImage(color_dst, "/home/nao/naoqi/color_dst", "jpg", seconds);

    // Now that you're done with the (local) image, you have to release it from the V.I.M.
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