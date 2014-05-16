#! /usr/bin/env lua

--[[ ######################################################################## #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: bluetoothCom.lua                                                  # #
# ########################################################################### #
# # Creation:   2014-04-29                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   # #
# #                                                                         # #
# ###########################################################################]]

require "socket"

function launchDistribution()
    os.execute("rfcomm connect hci0 20:13:11:12:05:89 &")

    tries = 0
    repeat 
        wSerialBT = io.open("/dev/rfcomm0", "w")
        rSerialBT = io.open("/dev/rfcomm0", "r")
        print("Connecting...")
        tries = tries + 1
        socket.select(nil, nil, 1)
    until (((wSerialBT ~= nil) and (rSerialBT ~= nil)) or tries > 10)

    if tries > 10 then
        print("Unable to connect")
        return 1
    end

    repeat
        wSerialBT:write("201")
        wSerialBT:flush()

        answer = rSerialBT:read()
        rSerialBT:flush()

        print("Initialzing connexion...")
        socket.select(nil, nil, 1)
    until tonumber(answer) == 202

    print("connexion initialized")

    repeat
        answer = rSerialBT:read()
        rSerialBT:flush()

        print("Waiting...")
        socket.select(nil, nil, 1)
    until tonumber(answer) == 200

    print("Finished!")

    return 0
end

launchDistribution()