# smart-heating-local [![Build Status](https://travis-ci.org/spiegelm/smart-heating-local.svg?branch=master)](https://travis-ci.org/spiegelm/smart-heating-local)

This is the repository for the local part of the Distributed System Laboratory project *An Infrastructure for Smart Residential Heating Systems*:

- [spiegelm/smart-heating-server](https://github.com/spiegelm/smart-heating-server)
- [**spiegelm/smart-heating-local**](https://github.com/spiegelm/smart-heating-local)
- [Octoshape/smart-heating-app](https://github.com/Octoshape/smart-heating-app)
- [spiegelm/smart-heating-report](https://github.com/spiegelm/smart-heating-report)

## Setup raspbian

Flash raspbian to a SD card and boot the Raspberry. Find the IP address using `nmap -sP [ip-adress]/[bitmask]`, e.g. `nmap -sP 192.168.0.0/24`.

Open a SSH client and connect to the determined IP. The default username and password are `pi` and `raspberry`.
Type `sudo raspi-config` to expand the filesystem, change the password and set the local time zone.

Enable IPv6: Add `ipv6` on a line by itself at the end of /etc/modules.

## Install dependencies

Install `at`. Needed to remain tunslip6 started because UDEV rules kill the spawning process.
```
sudo apt-get install at
```

### Install Python 3.4.1 and aiocoap

Credits to Marc Hüppin for the initial version.

openssl and libssl-dev are required for SSL support in python and is required by pip.

> sudo apt-get install sqlite3 libsqlite3-dev openssl libssl-dev
> 
> install the sqlite3 packages
> 
> ```
> mkdir ~/src
> cd ~/src
> wget https://www.python.org/ftp/python/3.4.1/Python-3.4.1.tgz
> ```
> 
> unpack
> cd into dir
> 
> ```
> ./configure
> make
> sudo make install
> ```
> 
> get the aiocoap library from github: https://github.com/chrysn/aiocoap
> 
> get setuptools from: https://pypi.python.org/pypi/setuptools
> 
> install aiocoap using
> ```
> python3.4 setup.py install
> ```

## Setup smart-heating-local

### Setup the border router connection

Clone this repository into your home folder: `git clone https://github.com/spiegelm/smart-heating-local.git`.

Create symbolic links

* udev rules: `sudo ln -s /home/pi/smart-heating-local/rules.d/90-local.rules /etc/udev/rules.d/`
* tunslip executable: `sudo ln -s /home/pi/smart-heating-local/bin/tunslip6 /bin/`

Add this line to `/etc/rc.local` to make sure the udev rule is also executed on startup
```
udevadm trigger --verbose --action=add --subsystem-match=usb --attr-match=idVendor=0403 --attr-match=idProduct=6001
```

TODO check the line above. It doesn't seem to be working.

Reboot: `sudo reboot`

Attach the sky tmote usb dongle to the raspberry. The tun0 interface should be shown by `ifconfig`.
In case of problems run `sudo ~/smart-heating-local/bin/start_tunslip.sh` manually.
Determine the ipv6 address of the web service: `less /var/log/tunslip6`:

```
Server IPv6 addresses:
 fdfd::212:7400:115e:a9e5
 fe80::212:7400:115e:a9e5
```

Retrieve the registered routes on the border router: `wget http://[fdfd::212:7400:115e:a9e5]`:
```
<html><head><title>ContikiRPL</title></head><body>
Neighbors<pre>fe80::221:2eff:ff00:22d3
</pre>Routes<pre>fdfd::221:2eff:ff00:22d3/128 (via fe80::221:2eff:ff00:22d3) 16711422s
</pre></body></html>
```

Test route to the thermostat by requesting the current temperature via coap-client (libcoap):
`~/smart-heating-local/bin/coap-client -m get coap://[fdfd::221:2eff:ff00:22d3]/sensors/temperature`
```
v:1 t:0 tkl:0 c:1 id:11708
22.49
```

Congratulations, your raspberry is connected to a thermostat!

### Install the required python packages

Install pip: https://pip.pypa.io/en/latest/installing.html

Install the project requirements:

```
cd ~/smart-heating-local/
pip install -r requirements.txt
```

### Configure cron tasks

Setup crontab to run the log and upload scripts periodically.

```
crontab -e
# Insert these lines at the end of the file:
*/15 * * * * /usr/local/bin/python3.4 /home/pi/smart-heating-local/thermostat_sync.py
*/5 * * * * /usr/local/bin/python3.4 /home/pi/smart-heating-local/server_sync.py
```

These commands ensure that the temperature is polled from the registered thermostats each 15 minutes and checked for uploading to the server each 5 minutes.
The scripts log interesting events to `~/smart-heating-local/logs/smart-heating.log`.
