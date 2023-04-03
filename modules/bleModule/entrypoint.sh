#!/bin/bash

cp dbus-org.bluez.service /etc/systemd/system/dbus-org.bluez.service
service dbus start
bluetoothd &

# python3 -u ./main.py

/bin/bash