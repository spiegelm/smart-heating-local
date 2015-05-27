#!/usr/bin/env python3

import subprocess
import sqlite3
import threading
import datetime
from multiprocessing import Pool
import re
import time
import json
# import urllib3

# Temperature regex (make sure we only match temperature)
temp_regex = r'\d{2}\.\d{1,2}'

def get_temperature(thermostat):
    mac = thermostat[0]
    url = 'coap://[fdfd::' + mac + ']/set/target'
    cmd = './bin/coap-client -m get ' + url + ' -B 30'
    print('cmd', cmd)
    timestamp = str(datetime.datetime.now())
    out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    print(out)
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
        cmd = "./bin/coap-client -m put coap://[fdfd::" + mac + "]/set/target -e '" + temperature +  "' -B 30"
        print('cmd', cmd)
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        print(out)
        # Check if the setting was successful
        _, _, temp = get_temperature(thermostat_setting)
        return mac, temp[0:-1] == temperature
    return mac, True

#  thermostats = [
#  ('221:2eff:ff00:228b', 'Bedroom'),
#  ]

# Static schedule
setpoints_day = [
('221:2eff:ff00:228b', '23.0'),
]

setpoints_night = [
('221:2eff:ff00:228b', '16.0'),
]

def main():
    # Create threadpool and run query
    pool = Pool(processes=5)

    # Try to get schedule from webofenergy server
    # try:
    #    json_schedule = urllib2.urlopen("http://webofenergy.inf.ethz.ch:8082/schedules").read()
    #    setpoints = json.loads(json_schedule)
    # # Otherwise fall back to static 6 a.m. to 10 p.m. schedule
    # except:
    start_setpoint = datetime.time(6,0,0)
    end_setpoint = datetime.time(22,0,0)
    now = datetime.datetime.now().time()
    if start_setpoint < now < end_setpoint:
        setpoints = setpoints_day
    else:
        setpoints = setpoints_night
    # Program thermostats
    result = pool.map(set_temperature, setpoints)
    print("result", result)

if __name__ == "__main__":
    main()

