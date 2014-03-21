/**************************************************************************** *
* *                  Nao Challenge 2014 Location Library                    * *
* *************************************************************************** *
* * File: NaoChallengeGeoloc.h                                              * *
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


#ifndef NAO_CHALLENGE_GEOLOC_H
# define NAO_CHALLENGE_GEOLOC_H
 /* Standard headers */
# include <array>
# include <iostream>
# include <math.h>
# include <string>
/* Boost headers */
# include <boost/shared_ptr.hpp>
 /* OpenCV headers */
# include <opencv2/core/core.hpp>
# include <opencv2/highgui/highgui.hpp>
# include <opencv2/imgproc/imgproc.hpp>
 /* Aldebaran headers */
# include <alcommon/albroker.h>
# include <alcommon/almodule.h>
# include <alcommon/alproxy.h>
# include <alproxies/altexttospeechproxy.h>
# include <alproxies/alvideodeviceproxy.h>
# include <qi/log.hpp>

namespace AL
{
//   // This is a forward declaration of AL:ALBroker which
//   // avoids including <alcommon/albroker.h> in this header
//   class ALBroker;
// }

/**
 * This class inherits AL::ALModule. This allows it to bind methods
 * and be run as a remote executable within NAOqi
 */
class NaoChallengeGeoloc : public AL::ALModule
{
    public:
        NaoChallengeGeoloc(boost::shared_ptr<ALBroker> broker,
                           const std::string &name);

        virtual ~NaoChallengeGeoloc();

        /**
        * Make Nao say a sentence given in argument.
        */
        void sayText(const std::string& toSay);

        /**
        * registerToVIM : Register to the V.I.M.
        */
        void registerToVideoDevice(const int &pResolution,
                                   const int &pColorSpace);

        /**
        * unRegisterFromVIM : Unregister from the V.I.M.
        */
        void unRegisterFromVideoDevice();

        /**
        * Ask Nao to follow the line.
        */
        void walkFromDmtxToDmtx(const int &fromDatamatrix,
                                const int &toDatamatrix);

        /**
        * Ask Nao to stop.
        */
        void stopWalk();

        /**
        * Get line diroection.
        */
        // void getDirection(cv::vector<cv::Vec4i> vectors);

        /**
        * saveImage : save the last image received.
        * @param pName name of the file
        */
        void saveImageLocal(const std::string& pName,
                            const std::string& imageFormat);

        /** Overloading ALModule::init().
        * This is called right after the module has been loaded
        */
        virtual void init();

        void exit();

    private:
        /**
        * Find line on image.
        */
        void findLine(bool &succeed,
                      cv::vector<cv::Vec4i> &lines,
                      long long &timeStamp);

        void directionFromVectors(cv::vector<cv::Vec4i> &lines,
                                  float &averageX,
                                  float &averageAngle);

        // Actually perform the cvSaveImage operation.
        void xSaveIplImage(const cv::Mat& img, const std::string& name,
                           const std::string& format,
                           int seconds);

        // ALProxies
        boost::shared_ptr<AL::ALProxy> speechProxy;
        boost::shared_ptr<AL::ALProxy> moveProxy;
        boost::shared_ptr<AL::ALProxy> postureProxy;

        // Proxy to the video input module.
        boost::shared_ptr<AL::ALVideoDeviceProxy> fCamProxy;

        // Nao's direction (in raidian):
        // std::float averageAngle;

        // Client name that is used to talk to the Video Device.
        std::string fVideoClientName;

        // This is set to true when we have subscribed one module to the VideoDevice.
        bool fRegisteredToVideoDevice;

        // Just a IplImage header to wrap around our camera image buffer.
        // This object doesn't own the image buffer.
        cv::Mat ImgSrc;

};
} // namespace AL

#endif // NAO_CHALLENGE_GEOLOC_H