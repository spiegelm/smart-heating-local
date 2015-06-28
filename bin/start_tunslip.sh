#!/bin/sh
sleep 2
# Check if tunnel interface is already up or establish one
ifconfig tun0 || sudo echo 'tunslip6 -s /dev/ttyUSB0 -c 25 fdfd::1/64 > /var/log/tunslip6' | at now
