#! /usr/bin/env sh

# ########################################################################### #
# #                          Nao Challenge 2014                             # #
# ########################################################################### #
# # File: bluetoothCom.sh                                                   # #
# ########################################################################### #
# # Creation:   2014-04-14                                                  # #
# #                                                                         # #
# # Team:       IUT de Cachan                                               # #
# #                                                                         # #
# # Author:     Nicolas SENAUD <nicolas at senaud dot fr>                   # #
# #                                                                         # #
# ########################################################################### #

rfcomm connect hci0 20:13:11:12:05:89 &

sleep 5

if ! ps -A | grep -w rfcomm 
then
	echo "Fatal Error: no Bluetooth connexion"
	exit
fi

echo 201 > /dev/rfcomm0

echo "Initializing connexion"

sleep 1

while ! awk '/./{line=$0} END{print line}' file.txt | grep 202
do
	echo 201 > /dev/rfcomm0
	echo "Retry..."
	sleep 1
done

echo "Connexion initialized"

while ! awk '/./{line=$0} END{print line}' file.txt | grep 200
do
	echo "Waiting..."
done

echo "Done"