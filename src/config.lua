#! /usr/bin/env lua

--[[ ######################################################################## #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: config.lua                                                        # #
# ########################################################################### #
# # Creation:   2014-05-01                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   # #
# #                                                                         # #
# ###########################################################################]]

function getConfigFromDmtx( fromDmtx )
    local angle = 0 -- degres
    local xDist = 0 -- meters
    local yDist = 0 -- meters

    if fromDmtx == 270 then
        angle = -45
        xDist =  0.3
        yDist = -0.3
    end

    return angle, xDist, yDist
end


function getConfigForCorrectionModule()
    local lineHysteresisLevel = 80 -- pixels
    local angleIfBeyondHysteresis = 12 -- degres
    local footstep = 0.05 -- meters
    local waitBetweenSteps = 500 -- milliseconds

    return lineHysteresisLevel, angleIfBeyondHysteresis, footstep,
           waitBetweenSteps
end