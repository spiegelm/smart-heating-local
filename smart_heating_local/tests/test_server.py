import unittest
import requests
from smart_heating_local.server import Server
from smart_heating_local.server_models import *


class ServerTestCase(unittest.TestCase):

    # TODO try requests-mock: https://pypi.python.org/pypi/requests-mock

    def setUp(self):
        self.server = Server()
        pass

    def test_get_local_mac_address(self):
        local_mac = self.server.get_local_mac_address()
        self.assertEqual(local_mac, 'b8:27:eb:ac:d0:8d')

    def test_get_thermostats_by_residence(self):
        local_mac = self.server.get_local_mac_address()

        raspberry = RaspberryDevice.load(mac=local_mac)
        thermostat_devices = raspberry.thermostat_devices

        self.assertEqual(len(thermostat_devices), 1)
        thermostat_device = thermostat_devices[0]
        self.assertIsInstance(thermostat_device, ThermostatDevice)
        self.assertEqual(thermostat_device.mac, '2e:ff:ff:00:22:8b')

    def test_get_heating_table(self):
        local_mac = self.server.get_local_mac_address()
        raspberry = RaspberryDevice.load(mac=local_mac)
        thermostat_devices = raspberry.thermostat_devices
        thermostat_device = thermostat_devices[0]

        response = requests.get(thermostat_device.thermostat.heating_table_url)
        heating_table = response.json()

        self.assertGreaterEqual(len(heating_table), 1)
        return heating_table

    def test_heating_table_entry_attributes(self):
        heating_table = self.test_get_heating_table()
        first_entry = heating_table[0]

        self.assertIsNotNone(first_entry.get('id', None))
        self.assertIsNotNone(first_entry.get('url', None))
        self.assertIsNotNone(first_entry.get('day', None))
        self.assertIsNotNone(first_entry.get('time', None))
        self.assertIsNotNone(first_entry.get('temperature', None))
        self.assertIsNotNone(first_entry.get('thermostat', None))
        self.assertIsInstance(first_entry.get('thermostat'), dict)
        self.assertIsNotNone(first_entry.get('thermostat').get('url', None))

if __name__ == '__main__':
    unittest.main()
