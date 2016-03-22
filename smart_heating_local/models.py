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

from datetime import datetime


class Measurement(object):
    """
    Base class for all types of measurements.
    """
    STATUS_NEW = 0
    STATUS_SENT = 1
    STATUS_ERROR = 2

    STATUSES = (
        STATUS_NEW,
        STATUS_SENT,
        STATUS_ERROR,
    )

    def __init__(self, mac, date, status, attempts):
        self.mac = mac
        self.date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        if status is None:
            status = self.STATUS_NEW
        assert status in self.STATUSES
        self.status = status
        self.attempts = attempts


class TemperatureMeasurement(Measurement):
    """
    Represents a temperature measurement.
    """

    def __init__(self, mac, date, temperature, status, attempts):
        super(TemperatureMeasurement, self).__init__(mac=mac, date=date, status=status, attempts=attempts)
        self.temperature = temperature

    def __repr__(self):
        return '<TemperatureMeasurement mac:"%s" date:"%s" temperature:"%s" status:"%s">' % (
        self.mac, self.date, self.temperature, self.status)


class MetaMeasurement(Measurement):
    """
    Represents a meta data measurement containing data about signal strength.
    """

    def __init__(self, mac, date, rssi, status, attempts):
        super(MetaMeasurement, self).__init__(mac=mac, date=date, status=status, attempts=attempts)
        self.rssi = rssi

    def __repr__(self):
        return '<MetaMeasurement mac:"%s" date:"%s" rssi:"%s" status:"%s">' % (
        self.mac, self.date, self.rssi, self.status)
