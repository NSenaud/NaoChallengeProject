#! /usr/bin/env lua

function getConfigFromDmtx( fromDmtx )
    local angle = 0
    local xDist = 0
    local yDist = 0

    if fromDmtx == 270 then
        angle = -45
        xDist =  0.3
        yDist = -0.3
    end

    return angle, xDist, yDist
end