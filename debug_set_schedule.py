#!/usr/bin/env python3
"""
Set the target temperature on all configured thermostats.
"""

from smart_heating_local import thermostat_controller

thermostat_controller.set_target_temperatures()
