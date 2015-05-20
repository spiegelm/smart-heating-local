import os
import shelve

class Config:
    PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__) + '/../')
    CONFIG_PATH = os.path.realpath(os.path.join(PROJECT_ROOT, 'data', 'config'))

    def __init__(self):
        with shelve.open(self.CONFIG_PATH) as config:
            self.__thermostat_macs = config.get('thermostat_macs', None)

    def get_thermostat_macs(self):
        return self.__thermostat_macs

    def save_thermostat_macs(self, thermostat_macs):
        with shelve.open(self.CONFIG_PATH) as config:
            config['thermostat_macs'] = thermostat_macs
            config.sync()
