#!/usr/bin/env python3
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

"""
Query, persist and control the temperature of configured thermostats.

For each configured thermostat query and persist the temperature measurements and meta data
and set the scheduled temperatures.
"""

from smart_heating_local import thermostat_controller

thermostat_controller.main()
