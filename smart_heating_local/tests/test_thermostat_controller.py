import unittest
from smart_heating_local.thermostat_controller import *
from nose.plugins.attrib import attr


class ThermostatControllerTestCase(unittest.TestCase):
    """
    Tests the processing of the API.
    This test relies on the server availability and certain data to be available. It is therefore
    not considered an isolated unit test but a system test which has been used during development.
    """

    def setUp(self):
        pass

    def test_ipv6(self):
        self.assertEqual(ipv6('2e:ff:ff:00:22:8b'), '2eff:ff00:228b')

    def test_coap_url(self):
        self.assertEqual(coap_url('2e:ff:ff:00:22:8b'), 'coap://[2eff:ff00:228b]')
