#!/usr/bin/env python3

import requests
import subprocess

server_url = 'http://52.28.68.182:8000/'


def main():

    thermostats = LinkedThermostats().get_thermostats_macs()
    print(thermostats)

class LinkedThermostats:

    def get_thermostats_macs(self):

        macs = []
        for rfid in self.get_thermostats_rfids():
            r = requests.get(server_url + 'device/thermostat/' + rfid)
            data = r.json()
            macs.append(data.get('mac'))

        return macs

    def get_thermostats_rfids(self):

        raspberry_mac = self.get_local_mac_address()
        lookup_url = server_url + 'device/raspberry/lookup/?mac=' + raspberry_mac
        r = requests.get(lookup_url)

        if r.status_code == 404:
            raise Exception('This raspberries MAC address has not been registered! '
                            'This should have happened before deployment')

        raspberry_data = r.json()
        residence_data = raspberry_data.get('residence')
        if residence_data is None:
            raise Exception('This raspberry has not been linked to a residence! '
                            'This should be done by the user!')

        thermostats = self.get_thermostats_by_residence(residence_data.get('url'))

        return thermostats

    def get_thermostats_by_residence(self, residence_url):
        rooms_url = residence_url + 'room/'
        r = requests.get(rooms_url)
        rooms = r.json()
        thermostats = []
        for room in rooms:
            thermostats.extend(self.get_thermostats_by_room(room.get('url')))

        return thermostats


    def get_thermostats_by_room(self, room_url):
        thermostats_url = room_url + 'thermostat/'
        r = requests.get(thermostats_url)
        thermostats = r.json()
        return thermostats


    def get_local_mac_address(self):
        """
        Captures the shell output of ifconfig and returns the first found MAC address
        """
        out_binary = subprocess.check_output('ifconfig', shell=True, stderr=subprocess.STDOUT)
        out = out_binary.decode('ascii')
        lines = out.split()

        hwaddr_index = None
        for index, item in enumerate(lines):
            # Find first occurrence of HWaddr
            if str(item) == 'HWaddr' and hwaddr_index is None:
                hwaddr_index = index

        if hwaddr_index is None:
            raise Exception('Could not find HWaddr in ifconfig output')

        mac = lines[hwaddr_index + 1]

        return mac



if __name__ == "__main__":
    main()
