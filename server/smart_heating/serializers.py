from django.forms import widgets
from rest_framework import serializers
from smart_heating.models import *


class ResidenceSerializer(serializers.HyperlinkedModelSerializer):
    rooms = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # rooms = serializers.HyperlinkedRelatedField(many=True, view_name='room-detail',
    #                                             lookup_url_kwarg='residence,room', read_only=True)
    room_base_url = serializers.HyperlinkedIdentityField(view_name='room-list', lookup_url_kwarg='residence')

    class Meta:
        model = Residence
        fields = ('rfid', 'url', 'room_base_url', 'rooms')
        # fields = ('url', 'rfid')


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    # This does not fill in
    # url = serializers.HyperlinkedIdentityField(view_name='room-detail', lookup_field='residence', lookup_url_kwarg='residence', read_only=True)

    class Meta:
        model = Room
        # fields = ('id', 'url', 'name', 'residence')
        fields = ('id', 'name', 'residence')


class ThermostatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thermostat
        fields = ('rfid', 'room')

