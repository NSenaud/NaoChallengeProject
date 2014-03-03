#ifndef NAO_CHALLENGE_GEOLOC_H
# define NAO_CHALLENGE_GEOLOC_H

# include <iostream>
# include <alcommon/almodule.h>
#include <alproxies/altexttospeechproxy.h>

namespace AL
{
  // This is a forward declaration of AL:ALBroker which
  // avoids including <alcommon/albroker.h> in this header
  class ALBroker;
}

/**
 * This class inherits AL::ALModule. This allows it to bind methods
 * and be run as a remote executable within NAOqi
 */
class NaoChallengeGeoloc : public AL::ALModule
{
public:
  NaoChallengeGeoloc(boost::shared_ptr<AL::ALBroker> broker,
           const std::string &name);

  virtual ~NaoChallengeGeoloc();

  /** Overloading ALModule::init().
    * This is called right after the module has been loaded
    */
    virtual void init();

    /**
    * Make Nao say a sentence given in argument.
    */
    void sayText(const std::string& toSay);

private:
    boost::shared_ptr<AL::ALProxy> speechProxy;

};

#endif // NAO_CHALLENGE_GEOLOC_H