#!/usr/bin/env python3
import json

import requests
import subprocess

class HttpError(Exception):
    def __init__(self, response, *args, permanent=False, **kwargs):
        self.permanent = permanent
        self.response = response

class NotFoundException(HttpError):
    pass

class Server:
    SERVER_URL = 'http://52.28.68.182:8000/'

    def thermostat_url(self, rfid=None):
        url = self.SERVER_URL + 'thermostat/'
        if rfid is not None:
            url += rfid + '/'
        return url

    def device_thermostat_url(self, rfid=None):
        url = self.SERVER_URL + 'device/thermostat/'
        if rfid is not None:
            url += rfid + '/'
        return url

    def device_thermostat_lookup_url(self, mac):
        return self.SERVER_URL + 'device/thermostat/lookup/?mac=%s' % mac

    def device_thermostat(self, rfid=None, mac=None):
        if (rfid is None) == (mac is None):
            raise Exception('Either rfid or mac is required')

        # Determine url
        if mac is not None:
            url = self.device_thermostat_lookup_url(mac)
        else:
            assert rfid is not None
            url = self.device_thermostat_url(rfid)

        r = requests.get(url)
        assert(200 <= r.status_code < 300)

        return r.json()

    def temperature_url(self, thermostat_url):
        return thermostat_url + 'temperature/'

    def upload_measurement(self, temperature_measurement):
        mac = temperature_measurement.mac
        device_thermostat = self.device_thermostat(mac=mac)

        thermostat_url = device_thermostat.get('thermostat').get('url')
        data = json.dumps({'datetime': temperature_measurement.date.isoformat(),
                'value': temperature_measurement.temperature})
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        r = requests.post(self.temperature_url(thermostat_url), data=data, headers=headers)

        if not (200 <= r.status_code < 300):
            # Handle error
            default_exception = HttpError('Failed to upload measurement %s, Result: %s %s' %
                                          (temperature_measurement, r.status_code, r.text))

            if r.status_code == 400:
                # TODO check for certain conditions that indicate a permanent error
                # e.g. r.json=={"datetime":["This field must be unique."]}
                # permanent_exception = default_exception
                # permanent_exception.permanent = True
                pass
            raise default_exception

    def get_thermostats_macs(self):

        macs = []
        for rfid in self.get_thermostats_rfids():
            r = requests.get(self.SERVER_URL + 'device/thermostat/' + rfid)
            data = r.json()
            macs.append(data.get('mac'))

        return macs

    def get_thermostats_rfids(self):

        raspberry_mac = self.get_local_mac_address()
        lookup_url = self.SERVER_URL + 'device/raspberry/lookup/?mac=' + raspberry_mac
        r = requests.get(lookup_url)

        if r.status_code == 404:
            raise Exception('This raspberries MAC address has not been registered! '
                            'This should have happened before deployment')

        raspberry_data = r.json()
        residence_data = raspberry_data.get('residence')
        if residence_data is None:
            raise Exception('This raspberry has not been linked to a residence! '
                            'This should be done by the user!')

        thermostats_data = raspberry_data.get('thermostat_devices')
        thermostats_rfids = [thermo.rfid for thermo in thermostats_data]

        return thermostats_rfids

    def get_thermostats_by_room(self, room_url):
        thermostats_url = room_url + 'thermostat/'
        r = requests.get(thermostats_url)
        thermostats = r.json()
        return thermostats

    def get_local_mac_address(self):
        """
        Captures the shell output of ifconfig and returns the first found MAC address
        """
        out_binary = subprocess.check_output('ifconfig', shell=True, stderr=subprocess.STDOUT)
        out = out_binary.decode('ascii')
        lines = out.split()

        hwaddr_index = None
        for index, item in enumerate(lines):
            # Find first occurrence of HWaddr
            if str(item) == 'HWaddr' and hwaddr_index is None:
                hwaddr_index = index

        if hwaddr_index is None:
            raise Exception('Could not find HWaddr in ifconfig output')

        mac = lines[hwaddr_index + 1]

        return mac
