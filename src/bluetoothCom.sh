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

while [ ! -c /dev/rfcomm0 ]
do
	sleep 1
	echo "Trying to connect..."
done

if ! ps -A | grep -w rfcomm 
then
	echo "Fatal Error: no Bluetooth connexion"
	exit
fi

cat /dev/rfcomm0 > /tmp/bluetooth.txt &

sleep 1

echo 201 > /dev/rfcomm0

echo "Initializing connexion"

while ! tail -2 /tmp/bluetooth.txt | grep 202
do
	echo 201 > /dev/rfcomm0
	echo "Retry..."
done

echo "Connexion initialized"

while ! tail -2 /tmp/bluetooth.txt | grep 200
do
	echo "Waiting..."
	sleep 1
done

killall rfcomm

echo "Finished!"