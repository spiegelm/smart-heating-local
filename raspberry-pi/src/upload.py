#!/usr/bin/env python3
import logging
import shelve

import sqlite3
import traceback

from models import TemperatureMeasurement
from server import Server
from server_models import RaspberryDevice
import sys
import requests

logging_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)
# logging.basicConfig(filename='upload.log', level=logging.INFO, format=logging_format)

log_formatter = logging.Formatter(logging_format)
root_logger = logging.getLogger()

file_handler = logging.FileHandler('upload.log')
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)


def download_linked_thermostats():

    logging.info('Fetch linked thermostats.')

    # Detect local mac address
    local_mac = Server().get_local_mac_address()

    # Get thermostat MACs
    raspberry = RaspberryDevice.load(mac=local_mac)
    thermostat_devices = raspberry.thermostat_devices
    thermostat_macs = [thermostat_device.mac for thermostat_device in thermostat_devices]

    with shelve.open('config') as config:
        config['thermostat_macs'] = thermostat_macs
        config.sync()
        logging.info('Wrote thermostat MACs to shelf "config".')
        config.close()


def upload_measurements():

    conn = sqlite3.connect('/home/pi/smart-heating/raspberry-pi/heating.db')
    get_temperatures_sql = 'SELECT * FROM heating_temperature WHERE status = %s' % TemperatureMeasurement.STATUS_NEW
    r = conn.execute(get_temperatures_sql)
    rows = r.fetchall()
    measurements = [TemperatureMeasurement(*row) for row in rows]

    # TODO improve error handling
    # test for internet connection first
    # handle unlinked or invalid thermostat MACs

    for measurement in measurements:
        update_status_sql = 'UPDATE heating_temperature SET status=:status WHERE mac=:mac AND timestamp=:date'
        try:
            Server().upload_measurement(measurement)
            conn.execute(update_status_sql, {'status': TemperatureMeasurement.STATUS_SENT, 'mac': measurement.mac, 'date': measurement.date})
            conn.commit()
            logging.info('upload successful: %s ' % repr(measurement))
        except requests.ConnectionError as e:
            # TODO maybe use our own exception (information hiding)
            # Log connection error but don't mark it as a permanent error
            logging.error('Could not upload: %s' % repr(measurement))
            logging.error('%s: %s' % (e.__class__.__name__, e))
        except Exception as e:
            # TODO update linked thermostats list. maybe we're trying to access a non linked thermostat
            # Don't mark as permanent error for now. Watch the logs what kind of errors these are
            # conn.execute(update_status_sql, {'status': TemperatureMeasurement.STATUS_ERROR, 'mac': measurement.mac, 'date': measurement.date})
            # conn.commit()
            logging.error('Could not upload: %s' % repr(measurement))
            logging.error(traceback.format_exc())

    conn.close()

def main():
    upload_measurements()
    download_linked_thermostats()


if __name__ == "__main__":
    main()
