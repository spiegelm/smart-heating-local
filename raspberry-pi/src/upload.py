#!/usr/bin/env python3

import sqlite3
import traceback

from models import TemperatureMeasurement
from server import Server


def main():

    conn = sqlite3.connect('/home/pi/smart-heating/raspberry-pi/heating.db')
    get_temperatures_sql = 'SELECT * FROM heating_temperature WHERE status = %s' % TemperatureMeasurement.STATUS_NEW
    r = conn.execute(get_temperatures_sql)
    rows = r.fetchall()
    measurements = [TemperatureMeasurement(*row) for row in rows]

    print(repr(measurements))

    for measurement in measurements:
        update_status_sql = 'UPDATE heating_temperature SET status=:status WHERE mac=:mac AND timestamp=:date'
        try:
            Server().upload_measurement(measurement)
            conn.execute(update_status_sql, {'status': TemperatureMeasurement.STATUS_SENT, 'mac': measurement.mac, 'date': measurement.date})
            conn.commit()
            print('uploaded %s successfully' % repr(measurement))
        except:
            conn.execute(update_status_sql, {'status': TemperatureMeasurement.STATUS_ERROR, 'mac': measurement.mac, 'date': measurement.date})
            conn.commit()
            print('error uploading %s' % repr(measurement))
            print(traceback.format_exc())

    conn.close()


if __name__ == "__main__":
    main()
