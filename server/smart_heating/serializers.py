from django.forms import widgets
from rest_framework import serializers
from smart_heating.models import Thermostat


class ThermostatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thermostat
        fields = ('rfid', 'temperature')
