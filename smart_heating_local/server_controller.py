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

import sqlite3
import traceback
from smart_heating_local.config import Config

from smart_heating_local.models import *
from smart_heating_local.server import Server
from smart_heating_local.server_models import RaspberryDevice
import requests

from smart_heating_local import logging

# Maximal number of attempts to send a measurement to the server after marking it as a permanent error.
MAX_ATTEMPTS = 5


def get_thermostat_devices():
    """
    Load the associated thermostat devices from the server.
    :return: List of thermostat device dictionaries associated to the local mac address
    :rtype: list[dict]
    """
    # Detect local mac address
    local_mac = Server().get_local_mac_address()

    # Get thermostat MACs
    raspberry = RaspberryDevice.load(mac=local_mac)
    thermostat_devices = raspberry.thermostat_devices

    return thermostat_devices


def download_linked_thermostats():
    """
    Load the list of associated thermostats from the server and store it in the config.
    """
    thermostat_devices = get_thermostat_devices()
    thermostat_macs = [thermostat_device.mac for thermostat_device in thermostat_devices]

    Config().save_thermostat_macs(thermostat_macs)
    logging.info('Wrote downloaded thermostat MACs to config.')


def download_heating_tables():
    """
    Load the heating tables of the associated thermostats from the server and store them in the config.
    """
    thermostat_devices = get_thermostat_devices()

    for thermostat_device in thermostat_devices:
        mac = thermostat_device.mac
        heating_table_url = thermostat_device.thermostat.heating_table_url

        # Request heating table
        response = requests.get(heating_table_url)
        assert (200 <= response.status_code < 300)
        heating_table_entries = response.json()

        current = Config().get_heating_table(mac)
        if current != heating_table_entries:
            # Save new schedule
            Config().save_heating_table(mac, heating_table_entries)
            logging.info("New config: Heating Table for %s" % mac)


def upload_temperatures():
    """
    Upload all remaining temperature measurements to the server.
    """

    with sqlite3.connect('/home/pi/smart-heating-local/data/heating.db') as conn:
        get_temperatures_sql = 'SELECT * FROM heating_temperature WHERE status = %s' % Measurement.STATUS_NEW
        rows = conn.execute(get_temperatures_sql).fetchall()
        measurements = [TemperatureMeasurement(*row) for row in rows]

        # Future work: improve error handling
        # Handle unlinked or invalid thermostat MACs

        # Test for internet connection first
        if not Server().is_connected():
            logging.error('Could not upload. No connection to the server.')
            return

        for measurement in measurements:
            update_status_sql = 'UPDATE heating_temperature SET status=:status, attempts=attempts+1 WHERE mac=:mac AND timestamp=:date'
            try:
                Server().upload_temperature_measurement(measurement)
                conn.execute(update_status_sql,
                             {'status': Measurement.STATUS_SENT, 'mac': measurement.mac, 'date': measurement.date})
                conn.commit()
                logging.info('upload successful: %s. Attempt #%s' % (repr(measurement), measurement.attempts))
            except requests.ConnectionError as e:
                # Log connection error but don't mark it as a permanent error
                conn.execute(update_status_sql,
                             {'status': Measurement.STATUS_NEW, 'mac': measurement.mac, 'date': measurement.date})
                conn.commit()
                logging.error('Could not upload: %s. Attempt #%s' % (repr(measurement), measurement.attempts))
                logging.error('%s: %s' % (e.__class__.__name__, e))
            except Exception as e:
                # Increase attempts. Mark as permanent error after to many attempts.
                status = Measurement.STATUS_NEW if measurement.attempts < MAX_ATTEMPTS else Measurement.STATUS_ERROR
                conn.execute(update_status_sql, {'status': status, 'mac': measurement.mac, 'date': measurement.date})
                conn.commit()
                logging.error('Could not upload: %s. Attempt #%s' % (repr(measurement), measurement.attempts))
                logging.error(traceback.format_exc())


def upload_meta_data():
    """
    Upload all remaining meta data entries to the server.
    """

    with sqlite3.connect('/home/pi/smart-heating-local/data/heating.db') as conn:
        get_meta_sql = 'SELECT * FROM heating_rssi WHERE status = %s' % Measurement.STATUS_NEW
        rows = conn.execute(get_meta_sql).fetchall()
        measurements = [MetaMeasurement(*row) for row in rows]

        # Future work: improve error handling
        # Handle unlinked or invalid thermostat MACs

        # Test for internet connection first
        if not Server().is_connected():
            logging.error('Could not upload. No connection to the server.')
            return

        for measurement in measurements:
            update_status_sql = 'UPDATE heating_rssi SET status=:status, attempts=attempts+1 WHERE mac=:mac AND timestamp=:date'
            try:
                Server().upload_meta_measurement(measurement)
                conn.execute(update_status_sql,
                             {'status': Measurement.STATUS_SENT, 'mac': measurement.mac, 'date': measurement.date})
                conn.commit()
                logging.info('upload successful: %s. Attempt #%s' % (repr(measurement), measurement.attempts))
            except requests.ConnectionError as e:
                # Log connection error but don't mark it as a permanent error
                conn.execute(update_status_sql,
                             {'status': Measurement.STATUS_NEW, 'mac': measurement.mac, 'date': measurement.date})
                conn.commit()
                logging.error('Could not upload: %s. Attempt #%s' % (repr(measurement), measurement.attempts))
                logging.error('%s: %s' % (e.__class__.__name__, e))
            except Exception as e:
                # Increase attempts. Mark as permanent error after to many attempts.
                status = Measurement.STATUS_NEW if measurement.attempts < MAX_ATTEMPTS else Measurement.STATUS_ERROR
                conn.execute(update_status_sql, {'status': status, 'mac': measurement.mac, 'date': measurement.date})
                conn.commit()
                logging.error('Could not upload: %s. Attempt #%s' % (repr(measurement), measurement.attempts))
                logging.error(traceback.format_exc())


def main():
    """
    Upload existing temperature and meta data and download current settings from the server.
    """
    upload_temperatures()
    upload_meta_data()
    download_linked_thermostats()
    download_heating_tables()
