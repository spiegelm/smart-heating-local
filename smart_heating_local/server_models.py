import requests


class Model(object):
    SERVER_URL = 'http://52.28.68.182:8000/'
    pass

class RaspberryDevice(Model):
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
        self.thermostat_devices = [ThermostatDevice(thermostat_json) for thermostat_json in json.get('thermostat_devices')]

    @staticmethod
    def load(rfid=None, mac=None):
        url = RaspberryDevice.__url(rfid=rfid, mac=mac)
        r = RaspberryDevice.requests.get(url)
        assert(200 <= r.status_code < 300)
        return RaspberryDevice(r.json())

    @staticmethod
    def __lookup_url(mac):
        url = RaspberryDevice.SERVER_URL + RaspberryDevice.RESOURCE_URL + RaspberryDevice.LOOKUP_MAC_SUFFIX_PATTERN.format(mac=mac)
        return url

    @staticmethod
    def __url(rfid=None, mac=None):
        if (rfid is None) == (mac is None):
            raise Exception('Either rfid or mac is required')

        if mac is not None:
            url = RaspberryDevice.SERVER_URL + RaspberryDevice.RESOURCE_URL + RaspberryDevice.LOOKUP_MAC_SUFFIX_PATTERN.format(mac=mac)
        else:
            assert rfid is not None
            url = RaspberryDevice.SERVER_URL + RaspberryDevice.RESOURCE_URL + rfid + '/'
        return url


class ThermostatDevice(Model):

    def __init__(self, json):
        self.rfid = json.get('rfid')
        self.mac = json.get('mac')
        self.url = json.get('url')
        self.thermostat = Thermostat(json.get('thermostat'))


class Residence(Model):
    def __init__(self, json):
        self.rfid = json.get('rfid')
        self.url = json.get('url')


class Thermostat(Model):
    def __init__(self, json):
        self.rfid = json.get('rfid')
        self.url = json.get('url')
        self.temperatures_url = json.get('temperatures_url')
