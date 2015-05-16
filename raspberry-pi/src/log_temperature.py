#!/usr/bin/env python3

import subprocess
import sqlite3
import threading
import datetime
from multiprocessing import Pool
import re
import time
import json
#import urllib2

# aiocoap imports
import logging
import asyncio
from aiocoap import *

import copy, sys


logging.basicConfig(level=logging.INFO)



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

@asyncio.coroutine
def get_temperature(thermostat):

    mac = thermostat[0]
    url = 'coap://[' + ipv6(mac) + ']/sensors/temperature'
    print(url)
    timestamp = str(datetime.datetime.now())

    protocol = yield from Context.create_client_context()
    
    request = Message(code=GET)
    request.set_request_uri(url)
    
    try:
        response = yield from protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        payload = str(response.payload, "utf-8") # sys.stdout.encoding
        print('Result: %s\n%r'%(response.code, payload))

        code = parse_coap_response_code(response.code)
        if 2 <= code < 3:
            temperature = float(response.payload)
            results.append([mac, timestamp, temperature])

    # if re.match(temp_regex, str(temperature)):
        # return mac, timestamp, temperature
    # else:
        # return mac, timestamp, "99.99"

@asyncio.coroutine
def get_heartbeat(thermostat):
    mac = thermostat[0]
    url = 'coap://[' + ipv6(mac) + ']/debug/heartbeat'
    timestamp = str(datetime.datetime.now())
    
    protocol = yield from Context.create_client_context()
    
    request = Message(code=GET)
    request.set_request_uri(url)
    
    try:
        response = yield from protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        payload = str(response.payload, "utf-8") # sys.stdout.encoding
        print('Result: %s\n%r'%(response.code, payload))

        code = parse_coap_response_code(response.code)    
        if code >= 2 and code < 3:
            version, uptime, rssi = map(lambda x: x.split(':')[1], str(payload).split(','))
            print (version, uptime, rssi)
            results.append([mac, timestamp, rssi])


def put_measurements(url, measurements):
   opener = urllib2.build_opener(urllib2.HTTPHandler)
   request = urllib2.Request(url, data=json.dumps(measurements))
   request.add_header('Content-Type', 'application/json')
   request.get_method = lambda: 'PUT'
   url = opener.open(request)


def execute_tasks(tasks):
    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    temp = copy.deepcopy(results)
    results.clear()
    return temp;


def main():
    # TODO get thermostat MACs via linked_thermostats.py

    thermostats = [ \
        ('2e:ff:ff:00:22:8b', 'Bedroom Michi'), \
        ('2e:ff:ff:00:22:8b', 'Bedroom Michi again'), \
    ]

    conn = sqlite3.connect('/home/pi/heating.db')

    # Make sure local tables are available
    create_temperature_table_sql = "CREATE TABLE IF NOT EXISTS heating_temperature \
                (mac CHAR(20), timestamp TIMESTAMP, temperature FLOAT);"
    create_rssi_table_sql = "CREATE TABLE IF NOT EXISTS heating_rssi \
                (mac CHAR(20), timestamp TIMESTAMP, rssi FLOAT);"
    conn.execute(create_temperature_table_sql)
    conn.execute(create_rssi_table_sql)
    conn.commit()

    # Create threadpool and run query
    # pool = Pool(processes=5)
    cur = conn.cursor()

    # temp_measurements = pool.map(get_temperature, thermostats)

    # Get temperature values
    temp_measurements = execute_tasks([asyncio.async(get_temperature(t)) for t in thermostats])
    # Execute tasks and wait
    for mac, ts, temp in temp_measurements:
        print (mac, ts, temp)


    new_values = ", ".join(["('" + mac + "','" + ts + "'," + str(temp) +")" for mac, ts, temp in temp_measurements])
    cur.execute("INSERT INTO heating_temperature (mac, timestamp, temperature) VALUES " + new_values + ";")

    # Get RSSI values
    rssi_measurements = execute_tasks([asyncio.async(get_heartbeat(t)) for t in thermostats])
    new_values = ", ".join(["('" + mac + "','" + ts + "'," + rssi +")" for mac, ts, rssi in rssi_measurements])
    cur.execute("INSERT INTO heating_rssi (mac, timestamp, rssi) VALUES " + new_values + ";")

    # Commit and close DB
    conn.commit()
    conn.close()

    # Finally upload data to webofenergy (do nothing if it doesn't work)
    #try:
       # put_measurements('http://webofenergy.inf.ethz.ch:8082/measurements/temperature', temp_measurements)
       # put_measurements('http://webofenergy.inf.ethz.ch:8082/measurements/rssi', rssi_measurements)
    # except:
       # pass


if __name__ == "__main__":
    main()
