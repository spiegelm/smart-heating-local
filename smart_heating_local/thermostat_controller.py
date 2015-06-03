import sqlite3
import asyncio
from asyncio.tasks import async
import aiocoap
from aiocoap import *

import copy
from smart_heating_local.config import Config
from smart_heating_local.models import *
from smart_heating_local import logging

# Temperature regex (make sure we only match temperature)
#temp_regex = r'\d{2}\.\d{2}'

# thread safe queue to store the results
from collections import deque
results = deque()

def parse_coap_response_code(response_code):
    response_code_class = response_code // 32
    response_code_detail = response_code % 32
    
    # compose response code
    return response_code_class + response_code_detail / 100 # returns a float
    #return str(response_code_class) + ".{:02d}".format(response_code_detail) # returns a string

def ipv6(mac_addr):
    # Convert MAC 2e:ff:ff:00:22:8b into IPv6 2eff:ff00:228b
    bytes = mac_addr.replace(':', '')
    ip = ''
    for index, part in enumerate(bytes):
        ip += part
        if index % 4 == 3 and index < len(bytes) - 1:
            ip += ':'
    # Prefix from border router
    return 'fdfd::221:' + ip

def coap_url(mac_addr):
    return 'coap://[' + ipv6(mac_addr) + ']'

def coap_request(url, method, payload=None):
    if payload is None:
        request_str = '%s %s' % (method, url)
    else:
        request_str = '%s %s "%s"' % (method, url, payload)
    logging.info(request_str)

    protocol = yield from Context.create_client_context()

    if isinstance(payload, float) or isinstance(payload, int):
        payload = str(payload)

    if payload is None:
        encoded_payload = b''
    elif isinstance(payload, str):
        encoded_payload = bytearray(payload, 'utf-8')
    else:
        raise Exception("Unexpected payload type")

    request = Message(code=method, payload=encoded_payload)
    request.set_request_uri(url)

    try:
        response = yield from protocol.request(request).response
    except aiocoap.error.RequestTimedOut as e:
        logging.error('Request timed out: %s' % request_str)
    except Exception as e:
        logging.error('Request failed: %s' % request_str)
        logging.exception(e)
        return None
    else:
        # Replace payload bytes with encoded string
        response.payload = str(response.payload, 'utf-8')
        logging.info('%s: %s, %r' % (request_str, response.code, response.payload))
        return response


@asyncio.coroutine
def get_temperature(thermostat_mac):
    url = coap_url(thermostat_mac) + '/sensors/temperature'
    timestamp = str(datetime.now())

    response = yield from async(coap_request(url, Code.GET))

    if response is not None:
        code = parse_coap_response_code(response.code)
        if 2 <= code < 3:
            temperature = float(response.payload)
            results.append([thermostat_mac, timestamp, temperature])


@asyncio.coroutine
def get_heartbeat(thermostat_mac):
    url = coap_url(thermostat_mac) + '/debug/heartbeat'
    timestamp = str(datetime.now())

    response = yield from async(coap_request(url, Code.GET))

    if response is not None:
        code = parse_coap_response_code(response.code)
        if 2 <= code < 3:
            version, uptime, rssi = map(lambda x: x.split(':')[1], str(response.payload).split(','))

            # TODO return version and uptime
            # print (version, uptime, rssi)

            # results.append({'mac': mac, 'timestamp': timestamp, 'rssi': rssi})
            results.append([thermostat_mac, timestamp, rssi])

def get_mode(thermostat_mac):
    url = coap_url(thermostat_mac) + '/set/mode'
    response = yield from async(coap_request(url, Code.GET))

    if response is not None:
        code = parse_coap_response_code(response.code)
        if 2 <= code < 3:
            return str(response.payload)
    return None


@asyncio.coroutine
def set_target_mode(mac):
    logging.info("Ensure target mode for %s" % mac)

    # Desired mode
    target_mode = 'manual target'

    # Check if the desired mode is already set
    current_mode = yield from async(get_mode(mac))
    if current_mode == target_mode:
        # Already set, nothing to do here
        return

    # Set mode
    url = coap_url(mac) + '/set/mode'
    response = yield from async(coap_request(url, Code.PUT, target_mode))

    if response is not None:
        code = parse_coap_response_code(response.code)
        if 2 <= code < 3:
            results.append({'payload': response.payload})


def get_target_temperature(mac):
    url = coap_url(mac) + '/set/target'
    response = yield from async(coap_request(url, Code.GET))

    if response is not None:
        code = parse_coap_response_code(response.code)
        if 2 <= code < 3:
            return float(response.payload)
    return None


@asyncio.coroutine
def set_target_temperature(mac, target_temperature):

    # Check if the desired target is already set
    current_target = yield from async(get_target_temperature(mac))
    if current_target == target_temperature:
        # Already set, nothing to do here
        return

    # Set target temperature
    url = coap_url(mac) + '/set/target'
    response = yield from async(coap_request(url, Code.PUT, target_temperature))

    result = dict()
    result['url'] = url
    if response is not None:
        code = parse_coap_response_code(response.code)
        result['code'] = code
        if 2 <= code < 3:
            result['target'] = target_temperature
    else:
        result['error'] = True
    results.append(result)


def execute_tasks(tasks):
    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    temp = copy.deepcopy(results)
    results.clear()
    return temp


def get_thermostats():
    # Load config from shelve
    config = Config()
    thermostat_macs = config.get_thermostat_macs()
    if thermostat_macs is None:
        # No thermostats configured
        # TODO may trigger a manual sync?
        logging.error('No thermostats defined in local config!')
        return
    # Store thermostats
    thermostats = [{'mac': mac} for mac in thermostat_macs]
    return thermostats


def log_temperatures():
    thermostats = get_thermostats()
    conn = sqlite3.connect('/home/pi/smart-heating-local/data/heating.db')

    # Make sure local tables are available
    create_temperature_table_sql = "CREATE TABLE IF NOT EXISTS heating_temperature (" \
                                   "mac CHAR(20) NOT NULL," \
                                   "timestamp TIMESTAMP NOT NULL," \
                                   "temperature FLOAT NOT NULL," \
                                   "status INTEGER NOT NULL);"
    create_rssi_table_sql = "CREATE TABLE IF NOT EXISTS heating_rssi (" \
                            "mac CHAR(20) NOT NULL," \
                            "timestamp TIMESTAMP NOT NULL," \
                            "rssi FLOAT NOT NULL);"
    conn.execute(create_temperature_table_sql)
    conn.execute(create_rssi_table_sql)
    conn.commit()

    cur = conn.cursor()

    # Get temperature values
    # Execute tasks and wait
    temp_measurements = execute_tasks([async(get_temperature(thermostat['mac'])) for thermostat in thermostats])

    if len(temp_measurements) > 0:
        new_values = ", ".join(["('" + mac + "','" + ts + "'," + str(temp) +"," + str(TemperatureMeasurement.STATUS_NEW) + ")"
                                for mac, ts, temp in temp_measurements])
        cur.execute("INSERT INTO heating_temperature (mac, timestamp, temperature, status) VALUES " + new_values + ";")

    # Get RSSI values
    rssi_measurements = execute_tasks([async(get_heartbeat(thermostat['mac'])) for thermostat in thermostats])

    if len(temp_measurements) > 0:
        new_values = ", ".join(["('" + mac + "','" + ts + "'," + rssi +")" for mac, ts, rssi in rssi_measurements])
        cur.execute("INSERT INTO heating_rssi (mac, timestamp, rssi) VALUES " + new_values + ";")

    # Commit and close DB
    conn.commit()
    conn.close()

    # Finally upload data (do nothing if it doesn't work)
    #try:
       # put_measurements('http://webofenergy.inf.ethz.ch:8082/measurements/temperature', temp_measurements)
       # put_measurements('http://webofenergy.inf.ethz.ch:8082/measurements/rssi', rssi_measurements)
    # except:
       # pass

def set_target_temperatures():
    thermostats = get_thermostats()

    # for thermostat in thermostats:
    #     heating_table = Config().get_heating_table(thermostat['mac'])

    # Ensure target mode is set
    modes = execute_tasks([asyncio.async(set_target_mode(thermostat['mac'])) for thermostat in thermostats])
    print(modes)

    # Set temperature values
    target_temperatures = execute_tasks([asyncio.async(set_target_temperature(thermostat['mac'], 25.5)) for thermostat in thermostats])
    print(target_temperatures)
