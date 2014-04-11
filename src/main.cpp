/**************************************************************************** *
* *                  Nao Challenge 2014 Location Library                    * *
* *************************************************************************** *
* * File: main.cpp                                                          * *
# *************************************************************************** *
* * Creation:   2014-02-27                                                  * *
* *                                                                         * *
* * Team:       IUT de Cachan                                               * *
* *                                                                         * *
* * Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   * *
* *                                                                         * *
* ****************************************************************************/


#include "NaoChallengeGeoloc.h"

#include <boost/shared_ptr.hpp>

#include <alcommon/albroker.h>
#include <alcommon/almodule.h>
#include <alcommon/albrokermanager.h>
#include <alcommon/altoolsmain.h>

// we're in a dll, so export the entry point
#ifdef _WIN32
# define ALCALL __declspec(dllexport)
#else
# define ALCALL
#endif

extern "C"
{
    ALCALL int _createModule(boost::shared_ptr<AL::ALBroker> broker)
    {
        // init broker with the main broker instance
        // from the parent executable
        AL::ALBrokerManager::setInstance(broker->fBrokerManager.lock());
        AL::ALBrokerManager::getInstance()->addBroker(broker);
        // create module instances
        AL::ALModule::createModule<AL::NaoChallengeGeoloc>(broker,
                                                       "NaoChallengeGeoloc");
        return 0;
    }

    ALCALL int _closeModule()
    {
        return 0;
    }
} // extern "C"