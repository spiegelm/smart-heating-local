# Create your views here.

from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse

from smart_heating.serializers import *


class ResidenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows residences to be viewed or edited.
    """
    queryset = Residence.objects.all()
    serializer_class = ResidenceSerializer


class RoomViewSet(viewsets.ModelViewSet):

    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    # TODO require the residence for all queries in a unified way

    def get_queryset(self, residence):
        queryset = Room.objects.filter(residence=residence)
        # http://stackoverflow.com/questions/21292646/capture-parameters-in-django-rest-framework
        # uid = self.kwargs.get(self.lookup_url_kwarg)
        return queryset


    def list(self, request, residence):
        queryset = self.get_queryset(residence)
        serializer = RoomSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, residence, pk):
        queryset = self.get_queryset(residence)
        user = get_object_or_404(queryset, pk=pk, residence=residence)
        serializer = RoomSerializer(user, context={'request': request})
        # TODO resolve the url via the RoomSerializer,
        # such that it can also be shown in the residence resource
        data = serializer.data
        # data['url'] = reverse('room-detail', args=[residence, pk], request=request)
        return Response(data)


class ThermostatViewSet(viewsets.ModelViewSet):

    queryset = Thermostat.objects.all()
    serializer_class = ThermostatSerializer

    def get_queryset(self, residence, room):
        # check residence and room
        get_object_or_404(Room.objects.all(), residence=residence, pk=room)
        return super(ThermostatViewSet, self).get_queryset()

    def list(self, request, residence, room):
        queryset = self.get_queryset(residence, room)
        list = queryset.all().filter(room=room)
        serializer = ThermostatSerializer(list, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, residence, room, pk):
        queryset = self.get_queryset(residence, room)
        # # check residence and room
        # get_object_or_404(Room.objects.all(), residence=residence, pk=room)
        thermostat = get_object_or_404(queryset, pk=pk, room=room)
        serializer = ThermostatSerializer(thermostat, context={'request': request})
        return Response(serializer.data)