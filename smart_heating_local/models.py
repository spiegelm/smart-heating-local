from datetime import datetime

class TemperatureMeasurement:

    STATUS_NEW = 0
    STATUS_SENT = 1
    STATUS_ERROR = 2

    STATUSES = (
        STATUS_NEW,
        STATUS_SENT,
        STATUS_ERROR,
    )

    def __init__(self, mac, date, temperature, status):
        self.mac = mac
        # self.date = datetime.strptime(date, 'YYYY-MM-DD HH:MM:SS.mmmmmm')
        self.date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        self.temperature = temperature
        if status is None:
            status = self.STATUS_NEW
        assert status in self.STATUSES
        self.status = status

    def __repr__(self):
        return '<TemperatureMeasurement mac:%s date:%s temperature:%s status:%s>' % (self.mac, self.date, self.temperature, self.status)
