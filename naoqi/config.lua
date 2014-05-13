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

    if fromDmtx == 220 then
        angle = 180
        xDist = 0.3
        yDist = 0
    end

    return angle, xDist, yDist
end


function distanceDependingOnDmtx( toDmtx )
    local dst = 0 -- 0 for infinite, else distance in meters
    local angle = 0 -- degres
    local xDist = 0 -- meters
    local yDist = 0 -- meters

    if toDmtx == 240 then -- Nao Gato
        dst = 2.0
        angle = -90
        xDist = 0
        yDist = 0.3
    end

    if toDmtx == 210 then -- Nao Maestro
        dst = 1.7
        angle = 75
        xDist = 0
        yDist = -0.2
    end

    if toDmtx == 220 then -- Nao Memento
        dst = 2.0
    end

    if toDmtx == 290 then -- Nao Memento
        dst = 1.2
        angle = -70
        yDist = 0.15
    end

    return dst, angle, xDist, yDist
end


function getConfigForCorrectionModule()
    local lineHysteresisLevel = 80 -- pixels
    local angleIfBeyondHysteresis = 12 -- degres
    local footstep = 0.05 -- meters
    local waitBetweenSteps = 500 -- milliseconds

    return lineHysteresisLevel, angleIfBeyondHysteresis, footstep,
           waitBetweenSteps
end
