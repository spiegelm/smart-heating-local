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
        self.assertEqual(ipv6('2e:ff:ff:00:22:8b'), 'fdfd::221:2eff:ff00:228b')

    def test_coap_url(self):
        self.assertEqual(coap_url('2e:ff:ff:00:22:8b'), 'coap://[fdfd::221:2eff:ff00:228b]')
