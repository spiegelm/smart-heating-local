#!/usr/bin/env python3

import sqlite3
import traceback

from models import TemperatureMeasurement
from server import Server
import sys
import requests


def main():

    conn = sqlite3.connect('/home/pi/smart-heating/raspberry-pi/heating.db')
    get_temperatures_sql = 'SELECT * FROM heating_temperature WHERE status = %s' % TemperatureMeasurement.STATUS_NEW
    r = conn.execute(get_temperatures_sql)
    rows = r.fetchall()
    measurements = [TemperatureMeasurement(*row) for row in rows]

    # print(repr(measurements))

    for measurement in measurements:
        update_status_sql = 'UPDATE heating_temperature SET status=:status WHERE mac=:mac AND timestamp=:date'
        try:
            Server().upload_measurement(measurement)
            conn.execute(update_status_sql, {'status': TemperatureMeasurement.STATUS_SENT, 'mac': measurement.mac, 'date': measurement.date})
            conn.commit()
            print('upload successful: %s ' % repr(measurement))
        except requests.ConnectionError as e:
            # TODO maybe use our own exception (information hiding)
            # Log connection error but don't mark it as a permanent error
            print('error uploading: %s' % repr(measurement), file=sys.stderr)
            print('ConnectionError: %s' % e)
        except Exception as e:
            # TODO update linked thermostats list. maybe we're trying to access a non linked thermostat
            # Don't mark as permanent error for now. Watch the logs what kind of errors these are
            # conn.execute(update_status_sql, {'status': TemperatureMeasurement.STATUS_ERROR, 'mac': measurement.mac, 'date': measurement.date})
            # conn.commit()
            print('error uploading %s' % repr(measurement), file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

    conn.close()


if __name__ == "__main__":
    main()
