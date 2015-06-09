import sqlite3
import traceback
from smart_heating_local.config import Config

from smart_heating_local.models import *
from smart_heating_local.server import Server
from smart_heating_local.server_models import RaspberryDevice
import requests

from smart_heating_local import logging

def get_thermostat_devices():
    # Detect local mac address
    local_mac = Server().get_local_mac_address()

    # Get thermostat MACs
    raspberry = RaspberryDevice.load(mac=local_mac)
    thermostat_devices = raspberry.thermostat_devices

    return thermostat_devices

def download_linked_thermostats():
    thermostat_devices = get_thermostat_devices()
    thermostat_macs = [thermostat_device.mac for thermostat_device in thermostat_devices]

    Config().save_thermostat_macs(thermostat_macs)
    logging.info('Wrote downloaded thermostat MACs to config.')

def download_heating_table():
    thermostat_devices = get_thermostat_devices()

    for thermostat_device in thermostat_devices:
        mac = thermostat_device.mac
        heating_table_url = thermostat_device.thermostat.heating_table_url

        # Request heating table
        response = requests.get(heating_table_url)
        assert(200 <= response.status_code < 300)
        heating_table_entries = response.json()

        current = Config().get_heating_table(mac)
        if current != heating_table_entries:
            # Save new schedule
            Config().save_heating_table(mac, heating_table_entries)
            logging.info("New config: Heating Table for %s" % mac)
            # TODO assign new temperature


def upload_temperatures():

    with sqlite3.connect('/home/pi/smart-heating-local/data/heating.db') as conn:
        get_temperatures_sql = 'SELECT * FROM heating_temperature WHERE status = %s' % Measurement.STATUS_NEW
        rows = conn.execute(get_temperatures_sql).fetchall()
        measurements = [TemperatureMeasurement(*row) for row in rows]

        # TODO improve error handling
        # handle unlinked or invalid thermostat MACs

        # Test for internet connection first
        if not Server().is_connected():
            logging.error('Could not upload. No connection to the server.')
            return

        for measurement in measurements:
            update_status_sql = 'UPDATE heating_temperature SET status=:status WHERE mac=:mac AND timestamp=:date'
            try:
                Server().upload_temperature_measurement(measurement)
                conn.execute(update_status_sql, {'status': Measurement.STATUS_SENT, 'mac': measurement.mac, 'date': measurement.date})
                conn.commit()
                logging.info('upload successful: %s ' % repr(measurement))
            except requests.ConnectionError as e:
                # Log connection error but don't mark it as a permanent error
                logging.error('Could not upload: %s' % repr(measurement))
                logging.error('%s: %s' % (e.__class__.__name__, e))
            except Exception as e:
                # TODO update linked thermostats list. maybe we're trying to access a non linked thermostat
                # Don't mark as permanent error for now. Watch the logs what kind of errors these are
                # conn.execute(update_status_sql, {'status': Measurement.STATUS_ERROR, 'mac': measurement.mac, 'date': measurement.date})
                # conn.commit()
                logging.error('Could not upload: %s' % repr(measurement))
                logging.error(traceback.format_exc())

def upload_meta_data():

    with sqlite3.connect('/home/pi/smart-heating-local/data/heating.db') as conn:
        get_meta_sql = 'SELECT * FROM heating_rssi WHERE status = %s' % Measurement.STATUS_NEW
        rows = conn.execute(get_meta_sql).fetchall()
        measurements = [MetaMeasurement(*row) for row in rows]

        # TODO improve error handling
        # handle unlinked or invalid thermostat MACs

        # Test for internet connection first
        if not Server().is_connected():
            logging.error('Could not upload. No connection to the server.')
            return

        for measurement in measurements:
            update_status_sql = 'UPDATE heating_rssi SET status=:status WHERE mac=:mac AND timestamp=:date'
            try:
                Server().upload_meta_measurement(measurement)
                conn.execute(update_status_sql, {'status': Measurement.STATUS_SENT, 'mac': measurement.mac, 'date': measurement.date})
                conn.commit()
                logging.info('upload successful: %s ' % repr(measurement))
            except requests.ConnectionError as e:
                # Log connection error but don't mark it as a permanent error
                logging.error('Could not upload: %s' % repr(measurement))
                logging.error('%s: %s' % (e.__class__.__name__, e))
            except Exception as e:
                # TODO update linked thermostats list. maybe we're trying to access a non linked thermostat
                # Don't mark as permanent error for now. Watch the logs what kind of errors these are
                # conn.execute(update_status_sql, {'status': Measurement.STATUS_ERROR, 'mac': measurement.mac, 'date': measurement.date})
                # conn.commit()
                logging.error('Could not upload: %s' % repr(measurement))
                logging.error(traceback.format_exc())

def main():
    upload_temperatures()
    upload_meta_data()
    download_linked_thermostats()
    download_heating_table()
