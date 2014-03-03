/* Project headers */
#include "NaoChallengeGeoloc.h"
/* Standard headers */
#include <iostream>
/* Aldebaran headers */
#include <alcommon/albroker.h>
#include <alcommon/alproxy.h>
#include <boost/shared_ptr.hpp>
#include <qi/log.hpp>
#include <alproxies/altexttospeechproxy.h>


NaoChallengeGeoloc::NaoChallengeGeoloc(boost::shared_ptr<AL::ALBroker> broker,
                                       const std::string& name)
                                       
                                       : AL::ALModule(broker, name)
{
  // Describe the module here. This will appear on the webpage
  setModuleDescription("The 2014's Nao Challege edition geolocalisation module");

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
  // We create a proxy for the ALTextToSpeech module
  speechProxy = getParentBroker()->getProxy("ALTextToSpeech");
  /**
   * setReturn(<return_name>, <return_description>);
   * This enables to document the return of the method.
   * It is not compulsory to write this line.
   */
}

NaoChallengeGeoloc::~NaoChallengeGeoloc() {}

void NaoChallengeGeoloc::init() {}


void NaoChallengeGeoloc::sayText(const std::string &toSay)
{
  std::cout << "Saying the phrase in the console..." << std::endl;
  std::cout << toSay << std::endl;
  
  try
  {
    speechProxy->callVoid("say", toSay);
    // speechProxy->callVoid("setParameter",
    //                       std::string("say"),
    //                       toSay);
  }
  
  catch(const AL::ALError&)
  {
    qiLogError("module.example") << "Could not get proxy to ALTextToSpeech" << std::endl;
  }
}