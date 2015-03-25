# smart-heating

# Setup a Raspberry Pi

Flash raspbian to a SD card and boot the Raspberry. Find the IP address using `nmap -sP [ip-adress]/[bitmask]`, e.g. `nmap -sP 192.168.0.0/24`.

Open a SSH client an connect to the determined IP. The default username and password are `pi` and `raspberry`.
Type `sudo raspi-config` to expand the filesystem and change the password.

Symbol link for udev rules: `sudo ln -s /home/pi/smart-heating/raspberry-pi/rules.d/90-local.rules /etc/udev/rules.d/`
