from django.forms import widgets
from rest_framework import serializers
from smart_heating.models import *


class ResidenceSerializer(serializers.HyperlinkedModelSerializer):
    #rooms = serializers.HyperlinkedRelatedField(
    #    queryset=Room.objects.all(), many=True, view_name='room-detail')

    class Meta:
        model = Residence
        # fields = ('url', 'rfid', 'rooms')
        fields = ('url', 'rfid')


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        #fields = ('url', 'id', 'name', 'residence')
        fields = ('id', 'name', 'residence')


class ThermostatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thermostat
        fields = ('rfid', 'room')

