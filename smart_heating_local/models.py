from datetime import datetime

class Measurement(object):
    STATUS_NEW = 0
    STATUS_SENT = 1
    STATUS_ERROR = 2

    STATUSES = (
        STATUS_NEW,
        STATUS_SENT,
        STATUS_ERROR,
    )

    def __init__(self, mac, date, status):
        self.mac = mac
        self.date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        if status is None:
            status = self.STATUS_NEW
        assert status in self.STATUSES
        self.status = status

class TemperatureMeasurement(Measurement):

    def __init__(self, mac, date, temperature, status):
        super(TemperatureMeasurement, self).__init__(mac=mac, date=date, status=status)
        self.temperature = temperature

    def __repr__(self):
        return '<TemperatureMeasurement mac:"%s" date:"%s" temperature:"%s" status:"%s">' % (self.mac, self.date, self.temperature, self.status)

class MetaMeasurement(Measurement):

    def __init__(self, mac, date, rssi, status):
        super(MetaMeasurement, self).__init__(mac=mac, date=date, status=status)
        self.rssi = rssi

    def __repr__(self):
        return '<MetaMeasurement mac:"%s" date:"%s" rssi:"%s" status:"%s">' % (self.mac, self.date, self.rssi, self.status)
