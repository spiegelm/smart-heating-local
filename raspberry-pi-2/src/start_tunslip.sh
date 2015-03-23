#!/bin/sh
sleep 2
sudo echo 'tunslip6 -s /dev/ttyUSB0 -c 25 fdfd::1/64 > /var/log/tunslip6' | at now
#echo 'tunslip6 -s /dev/ttyUSB0 -c 25 fdfd::1/64 >> /var/log/tunslip6' | at now
