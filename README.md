# Setup

## Setup raspbian

Flash raspbian to a SD card and boot the Raspberry. Find the IP address using `nmap -sP [ip-adress]/[bitmask]`, e.g. `nmap -sP 192.168.0.0/24`.

Open a SSH client and connect to the determined IP. The default username and password are `pi` and `raspberry`.
Type `sudo raspi-config` to expand the filesystem, change the password and set the local time zone.

## Setup smart-heating

Clone this repository into your home folder. It should now look like this:
```
pi@jpi ~/smart-heating $ ls
raspberry-pi  README.md
```

Install required software
```
sudo apt-get install at
```

Create symbolic links

* udev rules: `sudo ln -s /home/pi/smart-heating/raspberry-pi/rules.d/90-local.rules /etc/udev/rules.d/`
* tunslip executable: `sudo ln -s /home/pi/smart-heating/raspberry-pi/bin/tunslip6 /bin/`

TODO
