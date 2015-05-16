# Setup

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

## Setup smart-heating

Clone this repository into your home folder: `git clone https://github.com/spiegelm/smart-heating.git`. It should now look like this:
```
pi@jpi ~/smart-heating $ ls
raspberry-pi  README.md
```

Create symbolic links

* udev rules: `sudo ln -s /home/pi/smart-heating/raspberry-pi/rules.d/90-local.rules /etc/udev/rules.d/`
* tunslip executable: `sudo ln -s /home/pi/smart-heating/raspberry-pi/bin/tunslip6 /bin/`

Add this line to `/etc/rc.local` to make sure it is also executed on startup
```
udevadm trigger --verbose --action=add --subsystem-match=usb --attr-match=idVendor=0403 --attr-match=idProduct=6001
```

Reboot: `sudo reboot`

Attach the sky tmote usb dongle to the raspberry. The tun0 interface should be shown by `ifconfig`.  
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

Test route to the thermostat by requesting the current temperature via coap-client (libcoap): `~/smart-heating/raspberry-pi/bin/coap-client -m get coap://[fdfd::221:2eff:ff00:22d3]/sensors/temperature`
```
v:1 t:0 tkl:0 c:1 id:11708
22.49
```

Congratulations, your raspberry is connected to a thermostat!

### Install the required python packages

Install pip: https://pip.pypa.io/en/latest/installing.html

Install the project requirements:

```
cd ~/smart-heating/raspberry-pi/
pip install -r requirements.txt
```
