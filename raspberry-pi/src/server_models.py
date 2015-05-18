import requests


class Model(object):
    SERVER_URL = 'http://52.28.68.182:8000/'
    pass

class RaspberryDevice(Model):
    RESOURCE_URL = 'device/raspberry/'
    LOOKUP_MAC_SUFFIX_PATTERN = 'lookup?mac={mac}'

    # Attribute to allow dependency injection
    requests = requests

    def __init__(self, rfid=None, mac=None):
        url = self.__url(rfid=rfid, mac=mac)
        r = self.requests.get(url)
        assert(200 <= r.status_code < 300)

        self.__setup(r.json())

    def __setup(self, json):
        self.__json = json

        self.rfid = json.get('rfid')
        self.mac = json.get('mac')
        self.url = json.get('url')
        self.residence = json.get('residence')
        self.thermostat_devices = json.get('thermostat_devices')

    def __lookup_url(self, mac):
        url = self.SERVER_URL + self.RESOURCE_URL + self.LOOKUP_MAC_SUFFIX_PATTERN.format(mac=mac)
        return url

    def __url(self, rfid=None, mac=None):
        if (rfid is None) == (mac is None):
            raise Exception('Either rfid or mac is required')

        if mac is not None:
            url = self.SERVER_URL + self.RESOURCE_URL + self.LOOKUP_MAC_SUFFIX_PATTERN.format(mac=mac)
        else:
            assert rfid is not None
            url = self.SERVER_URL + self.RESOURCE_URL + rfid + '/'
        return url