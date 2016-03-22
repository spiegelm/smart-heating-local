"""
Copyright 2016 Michael Spiegel, Wilhelm Kleiminger

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import requests


class Model(object):
    """
    Base class for server models.
    """
    SERVER_URL = 'http://52.28.68.182:8000/'
    pass


class RaspberryDevice(Model):
    """
    Represents a physical raspberry device.
    """
    RESOURCE_URL = 'device/raspberry/'
    LOOKUP_MAC_SUFFIX_PATTERN = 'lookup?mac={mac}'

    # Attribute to allow dependency injection
    requests = requests

    def __init__(self, json):
        self.__json = json

        self.rfid = json.get('rfid')
        self.mac = json.get('mac')
        self.url = json.get('url')
        self.residence = Residence(json.get('residence'))
        self.thermostat_devices = [ThermostatDevice(thermostat_json) for thermostat_json in
                                   json.get('thermostat_devices')]

    @staticmethod
    def load(rfid=None, mac=None):
        """
        :param rfid: RFID to identify the raspberry
        :param mac: MAC address to identify the raspberry
        :return: The associated raspberry device
        """
        url = RaspberryDevice.__url(rfid=rfid, mac=mac)
        r = RaspberryDevice.requests.get(url)
        assert (200 <= r.status_code < 300)
        return RaspberryDevice(r.json())

    @staticmethod
    def __lookup_url(mac):
        """
        :param mac: Raspberry MAC address to look for
        :type mac: str
        :return: The URL to query the raspberry device with the given MAC address
        """
        url = RaspberryDevice.SERVER_URL + RaspberryDevice.RESOURCE_URL + RaspberryDevice.LOOKUP_MAC_SUFFIX_PATTERN.format(
            mac=mac)
        return url

    @staticmethod
    def __url(rfid=None, mac=None):
        """
        :param rfid: The Raspberry RFID number
        :param mac: The Raspberry MAC address
        :return: The URL to query the raspberry device with the given RFID or MAC address
        """
        if (rfid is None) == (mac is None):
            raise Exception('Either rfid or mac is required')

        if mac is not None:
            url = RaspberryDevice.SERVER_URL + RaspberryDevice.RESOURCE_URL + RaspberryDevice.LOOKUP_MAC_SUFFIX_PATTERN.format(
                mac=mac)
        else:
            assert rfid is not None
            url = RaspberryDevice.SERVER_URL + RaspberryDevice.RESOURCE_URL + rfid + '/'
        return url


class ThermostatDevice(Model):
    """
    Represents a physical thermostat device.
    """

    def __init__(self, json):
        self.rfid = json.get('rfid')
        self.mac = json.get('mac')
        self.url = json.get('url')
        self.thermostat = Thermostat(json.get('thermostat'))


class Residence(Model):
    """
    Represents a residence.
    """

    def __init__(self, json):
        self.rfid = json.get('rfid')
        self.url = json.get('url')


class Thermostat(Model):
    """
    Represents a thermostat.
    """

    def __init__(self, json):
        self.rfid = json.get('rfid')
        self.url = json.get('url')
        self.temperatures_url = json.get('temperatures_url')
        self.heating_table_url = json.get('heating_table_url')
