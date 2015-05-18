#!/usr/bin/env python3

import unittest
from server import Server
from server_models import RaspberryDevice


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

        raspberry = RaspberryDevice(mac=local_mac)
        self.assertEqual(len(raspberry.thermostat_devices), 1)
        self.assertEqual(raspberry.thermostat_devices[0].get('mac'), '2e:ff:ff:00:22:8b')


if __name__ == '__main__':
    unittest.main()
