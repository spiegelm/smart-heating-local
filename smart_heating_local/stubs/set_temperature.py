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
temp_regex = r'\d{2}\.\d{1,2}'

def get_temperature(thermostat):
   mac = thermostat[0]
   url = 'coap://[fdfd::' + mac + ']/set/target' 
   cmd = 'coap-client -m get ' + url + ' -B 30'
   timestamp = str(datetime.datetime.now())
   out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
   lines = out.split()
   temperature = lines[-1].strip()
   if re.match(temp_regex, str(temperature)):
      return mac, timestamp, temperature
   else:
      return mac, timestamp, "99.99"

def set_temperature(thermostat_setting):
   temperature = thermostat_setting[1]
   mac = thermostat_setting[0]
   # Check if temperature already set
   _, _, temp = get_temperature(thermostat_setting)
   if temp[0:-1] != temperature:
      cmd = "coap-client -m put coap://[fdfd::" + mac + "]/set/target -e '" + temperature +  "' -B 30"
      out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
      # Check if the setting was successful
      _, _, temp = get_temperature(thermostat_setting)
      return (mac, temp[0:-1] == temperature)
   return (mac, True)

#  thermostats = [ \
#  ('221:2eff:ff00:22d2', 'First floor WC'), \
#  ('221:2eff:ff00:22d6', 'Bedroom Lisa'), \
#  ('221:2eff:ff00:22d1', 'Bedroom Willi'), \
#  ('221:2eff:ff00:22dc', 'Bedroom parents'), \
#  ('250:c2ff:ff18:8d34', 'Dining room (Wall)'), \
#  ('221:2eff:ff00:2294', 'Dining room (Window)'), \
#  ('221:2eff:ff00:228b', 'Entrance'), \
#  ('221:2eff:ff00:2282', 'First floor corridor'), \
#  ('221:2eff:ff00:22ce', 'Ground floor WC'), \
#  ('221:2eff:ff00:2287', 'Ground floor study'), \
#  ('221:2eff:ff00:22d7', 'Living room / Fireplace'), \
#  ('221:2eff:ff00:2288', 'Fireplace'), \
#  ('221:2eff:ff00:2293', 'Living room'), \
#  ('221:2eff:ff00:22d0', 'First floor study') \
#  ]

# Static schedule
setpoints_day = [ \
('221:2eff:ff00:22d2', '21.0'), \
('221:2eff:ff00:22d6', '18.0'), \
('221:2eff:ff00:22d1', '21.0'), \
('221:2eff:ff00:22dc', '19.0'), \
('250:c2ff:ff18:8d34', '21.0'), \
('221:2eff:ff00:2294', '21.0'), \
('221:2eff:ff00:228b', '17.0'), \
('221:2eff:ff00:2282', '19.0'), \
('221:2eff:ff00:22ce', '21.0'), \
('221:2eff:ff00:2287', '21.0'), \
('221:2eff:ff00:22d7', '21.0'), \
('221:2eff:ff00:2288', '21.0'), \
('221:2eff:ff00:2293', '21.0'), \
('221:2eff:ff00:22d0', '21.0') \
]

setpoints_night = [ \
('221:2eff:ff00:22d2', '16.0'), \
('221:2eff:ff00:22d6', '16.0'), \
('221:2eff:ff00:22d1', '16.0'), \
('221:2eff:ff00:22dc', '16.0'), \
('250:c2ff:ff18:8d34', '16.0'), \
('221:2eff:ff00:2294', '16.0'), \
('221:2eff:ff00:228b', '16.0'), \
('221:2eff:ff00:2282', '16.0'), \
('221:2eff:ff00:22ce', '16.0'), \
('221:2eff:ff00:2287', '16.0'), \
('221:2eff:ff00:22d7', '16.0'), \
('221:2eff:ff00:2288', '16.0'), \
('221:2eff:ff00:2293', '16.0'), \
('221:2eff:ff00:22d0', '16.0') \
]

def main():
   # Create threadpool and run query
   pool = Pool(processes=5)

   # Try to get schedule from webofenergy server
   try:
      json_schedule = urllib2.urlopen("http://webofenergy.inf.ethz.ch:8082/schedules").read()
      setpoints = json.loads(json_schedule)
   # Otherwise fall back to static 6 a.m. to 10 p.m. schedule
   except:
      start_setpoint = datetime.time(6,0,0)
      end_setpoint = datetime.time(22,0,0)
      now = datetime.datetime.now().time()
      if start_setpoint < now and now < end_setpoint:
	 setpoints = setpoints_day
      else:
	 setpoints = setpoints_night
   # Program thermostats
   result = pool.map(set_temperature, setpoints)

if __name__ == "__main__":
   main()

