#!/usr/bin/env python3
"""
Query, persist and control the temperature of configured thermostats.

For each configured thermostat query and persist the temperature measurements and meta data
and set the scheduled temperatures.
"""

from smart_heating_local import thermostat_controller

thermostat_controller.main()
