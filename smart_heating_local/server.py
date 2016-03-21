import json

import requests
import subprocess


class Error(Exception):
    def __init__(self, response, *args, permanent=False, **kwargs):
        self.permanent = permanent
        self.response = response


class NotFoundException(Error):
    pass


class Server:
    """
    Interface for server communication.
    """
    SERVER_URL = 'http://52.28.68.182:8000/'

    def thermostat_url(self, rfid=None):
        """
        Return the URL of a thermostats API endpoint.
        :type rfid: str
        :rtype: str
        """
        url = self.SERVER_URL + 'thermostat/'
        if rfid is not None:
            url += rfid + '/'
        return url

    def device_thermostat_url(self, rfid=None):
        """
        Return the URL of a device thermostats API endpoint.
        :rtype: str
        """
        url = self.SERVER_URL + 'device/thermostat/'
        if rfid is not None:
            url += rfid + '/'
        return url

    def device_thermostat_lookup_url(self, mac):
        """
        Return the URL to lookup a device thermostat by its MAC address.
        :rtype: str
        """
        return self.SERVER_URL + 'device/thermostat/lookup/?mac=%s' % mac

    def device_thermostat(self, rfid=None, mac=None):
        """
        Look up the device thermostat by its RFID or MAC address and return it.
        :return: The servers JSON response as a dict object.
        :rtype: dict
        """
        if (rfid is None) == (mac is None):
            raise Exception('Either rfid or mac is required')

        # Determine url
        if mac is not None:
            url = self.device_thermostat_lookup_url(mac)
        else:
            assert rfid is not None
            url = self.device_thermostat_url(rfid)

        r = requests.get(url)
        assert (200 <= r.status_code < 300)

        return r.json()

    def temperature_url(self, thermostat_url):
        """
        Return the URL of the temperature collection endpoint.
        """
        return thermostat_url + 'temperature/'

    def meta_url(self, thermostat_url):
        """
        Return the URL of the meta data collection endpoint.
        """
        return thermostat_url + 'meta_entry/'

    def is_connected(self):
        """
        :return: Whether the server is accessible
        :rtype: bool
        """
        try:
            r = requests.get(self.SERVER_URL)
        except requests.ConnectionError:
            return False
        else:
            return True

    def upload_temperature_measurement(self, temperature_measurement):
        """
        Upload a temperature measurement.
        :type temperature_measurement: smart_heating_local.models.TemperatureMeasurement
        :raise Error: If upload failed
        """
        mac = temperature_measurement.mac
        device_thermostat = self.device_thermostat(mac=mac)

        thermostat_url = device_thermostat.get('thermostat').get('url')
        data = json.dumps({'datetime': temperature_measurement.date.isoformat(),
                           'value': temperature_measurement.temperature})
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        r = requests.post(self.temperature_url(thermostat_url), data=data, headers=headers)

        if not (200 <= r.status_code < 300):
            # Handle error
            default_exception = Error('Failed to upload measurement %s, Result: %s %s' %
                                      (temperature_measurement, r.status_code, r.text))

            raise default_exception

    def upload_meta_measurement(self, meta_measurement):
        """
        Upload a meta measurement.
        :type meta_measurement: smart_heating_local.models.MetaMeasurement
        :raise Error: If upload fails
        """
        mac = meta_measurement.mac
        device_thermostat = self.device_thermostat(mac=mac)

        thermostat_url = device_thermostat.get('thermostat').get('url')
        data = json.dumps({'datetime': meta_measurement.date.isoformat(),
                           'rssi': meta_measurement.rssi})
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        r = requests.post(self.meta_url(thermostat_url), data=data, headers=headers)

        if not (200 <= r.status_code < 300):
            # Handle error
            default_exception = Error('Failed to upload measurement %s, Result: %s %s' %
                                      (meta_measurement, r.status_code, r.text))
            raise default_exception

    def get_thermostats_macs(self):
        """
        Query and return the list of associated thermostat MAC addresses.
        :rtype: list[str]
        """
        macs = []
        for rfid in self.get_thermostats_rfids():
            r = requests.get(self.SERVER_URL + 'device/thermostat/' + rfid)
            data = r.json()
            macs.append(data.get('mac'))

        return macs

    def get_thermostats_rfids(self):
        """
        Query and return the List of thermostat RFIDs associated to the local MAC address.
        :return: List of thermostat RFIDs
        :rtype: list[str]
        """
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
        thermostats_rfids = [thermostat.rfid for thermostat in thermostats_data]

        return thermostats_rfids

    def get_thermostats_by_room(self, room_url):
        """
        Query and return the list of a rooms thermostats.
        :type room_url: str
        :return: List of thermostat dictionaries.
        :rtype: list[dict]
        """
        thermostats_url = room_url + 'thermostat/'
        r = requests.get(thermostats_url)
        thermostats = r.json()
        return thermostats

    def get_local_mac_address(self):
        """
        Capture the shell output of ifconfig and return the first found MAC address.
        :return: The local MAC address
        :rtype: str
        """
        out_binary = subprocess.check_output('/sbin/ifconfig', shell=True, stderr=subprocess.STDOUT)
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
