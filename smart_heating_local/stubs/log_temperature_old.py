#!/usr/bin/python
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

import subprocess
import sqlite3
import threading
import datetime
from multiprocessing import Pool
import re
import time
import json
import urllib2

# Temperature regex (make sure we only match temperature)
temp_regex = r'\d{2}\.\d{2}'

def get_temperature(thermostat):
   mac = thermostat[0]
   url = 'coap://[fdfd::' + mac + ']/sensors/temperature' 
   cmd = 'coap-client -m get ' + url
   timestamp = str(datetime.datetime.now())
   out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
   lines = out.split()
   temperature = lines[-1].strip()
   if re.match(temp_regex, str(temperature)):
      return mac, timestamp, temperature
   else:
      return mac, timestamp, "99.99"

def get_heartbeat(thermostat):
   mac = thermostat[0]
   url = 'coap://[fdfd::' + mac + ']/debug/heartbeat'
   cmd = 'coap-client -m get ' + url
   timestamp = str(datetime.datetime.now())
   try:
      out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
      lines = out.split()
      payload =  lines[-1].strip()
      version, uptime, rssi = map(lambda x: x.split(':')[1], payload.split(','))
      return mac, timestamp, rssi
   except:
      return mac, timestamp, '0'

def put_measurements(url, measurements):
   opener = urllib2.build_opener(urllib2.HTTPHandler)
   request = urllib2.Request(url, data=json.dumps(measurements))
   request.add_header('Content-Type', 'application/json')
   request.get_method = lambda: 'PUT'
   url = opener.open(request)

thermostats = [ \
('221:2eff:ff00:22d2', 'First floor WC'), \
('221:2eff:ff00:22d6', 'Bedroom Lisa'), \
('221:2eff:ff00:22d1', 'Bedroom Willi'), \
('221:2eff:ff00:22dc', 'Bedroom parents'), \
('250:c2ff:ff18:8d34', 'Dining room (Wall)'), \
('221:2eff:ff00:2294', 'Dining room (Window)'), \
('221:2eff:ff00:228b', 'Entrance'), \
('221:2eff:ff00:2282', 'First floor corridor'), \
('221:2eff:ff00:22ce', 'Ground floor WC'), \
('221:2eff:ff00:2287', 'Ground floor study'), \
('221:2eff:ff00:22d7', 'Living room / Fireplace'), \
('221:2eff:ff00:2288', 'Fireplace'), \
('221:2eff:ff00:2293', 'Living room'), \
('221:2eff:ff00:22d0', 'First floor study') \
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
pool = Pool(processes=5)
cur = conn.cursor()

# Get temperature values
temp_measurements = pool.map(get_temperature, thermostats)
new_values = ", ".join(["('" + mac + "','" + ts + "'," + temp +")" for mac, ts, temp in temp_measurements])
cur.execute("INSERT INTO heating_temperature (mac, timestamp, temperature) VALUES " + new_values + ";")

# Get RSSI values
rssi_measurements = pool.map(get_heartbeat, thermostats)
new_values = ", ".join(["('" + mac + "','" + ts + "'," + rssi +")" for mac, ts, rssi in rssi_measurements])
cur.execute("INSERT INTO heating_rssi (mac, timestamp, rssi) VALUES " + new_values + ";")

# Commit and close DB
conn.commit()
conn.close()

# Finally upload data to webofenergy (do nothing if it doesn't work)
try:
   put_measurements('http://webofenergy.inf.ethz.ch:8082/measurements/temperature', temp_measurements)
   put_measurements('http://webofenergy.inf.ethz.ch:8082/measurements/rssi', rssi_measurements)
except:
   pass

