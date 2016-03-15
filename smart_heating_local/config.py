import os
import shelve


class Config:
    """
    Responsible for persisting configuration like associated thermostat MAC addresses and heating tables.
    """
    PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__) + '/..')
    CONFIG_PATH = os.path.realpath(PROJECT_ROOT + '/data/config')

    THERMOSTAT_MACS = 'thermostat_macs'
    HEATING_TABLES = 'heating_tables'

    def get_thermostat_macs(self):
        """
        Retrieve the list of stored thermostat MAC addresses.
        :rtype: List[str]
        """
        with shelve.open(self.CONFIG_PATH) as config:
            return config.get(self.THERMOSTAT_MACS, None)

    def save_thermostat_macs(self, thermostat_macs):
        """
        Store a list of thermostat MAC addresses in the config file.
        :type thermostat_macs: List[str]
        """
        with shelve.open(self.CONFIG_PATH) as config:
            config[self.THERMOSTAT_MACS] = thermostat_macs
            # Write to file
            config.sync()

    def get_heating_table(self, thermostat_mac):
        """
        Retrieve a thermostats heating schedule
        :type thermostat_mac: str
        :rtype: List[dict]
        """
        with shelve.open(self.CONFIG_PATH) as config:
            tables = config.get(self.HEATING_TABLES, None)
            if tables is None:
                return []
            else:
                return config.get(self.HEATING_TABLES).get(thermostat_mac, [])

    def save_heating_table(self, thermostat_mac, heating_table_entries):
        """
        Store a thermostats heating schedule in the config file.
        :type thermostat_mac: str
        :type heating_table_entries: List[dict]
        """
        with shelve.open(self.CONFIG_PATH) as config:
            # Ensure config is a dict
            current_tables = config.get(self.HEATING_TABLES, None)
            if current_tables is None or not isinstance(current_tables, dict):
                current_tables = dict()

            current_tables[thermostat_mac] = heating_table_entries
            config[self.HEATING_TABLES] = current_tables
            config.sync()
