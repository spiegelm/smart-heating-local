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

import time
import gdata.spreadsheet.service
import subprocess
import datetime
import os

email = 'heatinglog@gmail.com'
password = 'ZDMzZTFlNTVmYzEzMGJmNmNmZWNkZGY1'
spreadsheet_key = '0AjTqQG-ZZQOidGdhUFFIdDRuTVNNMlZnczh0RVoyenc'
worksheet_id = 'od6'

spr_client = gdata.spreadsheet.service.SpreadsheetsService()
spr_client.email = email
spr_client.password = password
spr_client.source = 'Python logger'
spr_client.ProgrammaticLogin()

# SD
cmd = 'df | grep "rootfs"'
mem = subprocess.check_output(cmd, shell=True)
fs, size, used_mem, free_mem, use_percentage, mountpoint = mem.strip().split()
# RAM
cmd = 'free -t | egrep "Mem"'
ram = subprocess.check_output(cmd, shell=True)
_, total, used_ram, free_ram, _, _, _ = ram.strip().split()
# Processes
cmd = 'top -b -n 1 | egrep "(cf-proxy)|(java)|(tunslip6)" | awk \' { print ( $NF ) }\''
proc = subprocess.check_output(cmd, shell=True)
processes = ",".join(proc.split())
# Load
cmd = 'cat /proc/loadavg'
load = subprocess.check_output(cmd, shell=True)
avg_load_1_min, avg_load_5_min, avg_load_15_min, runnable, last_pid = load.strip().split()

# Prepare the dictionary to write
row = {}
row['timestamp'] = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
row['freeram'] = free_ram
row['usedram'] = used_ram
row['freemem'] = free_mem
row['usedmem'] = used_mem
row['avgload1min'] = avg_load_1_min
row['avgload5min'] = avg_load_5_min
row['avgload15min'] = avg_load_15_min
row['processes'] = processes
row['dbsize'] = str(os.path.getsize('/home/pi/heating.db'))

entry = spr_client.InsertRow(row, spreadsheet_key, worksheet_id)
if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
  pass
  #print "[PythonSysLogger] Successfully uploaded record to Google Docs."
else:
  print "[PythonSysLogger] [Fail] Problem uploading record to Google Docs."

