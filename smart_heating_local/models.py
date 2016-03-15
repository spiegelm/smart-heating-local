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
