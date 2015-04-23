# Create your views here.

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import viewsets
from rest_framework.response import Response

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

    def list(self, request, residence):
        queryset = self.get_queryset()
        list = get_list_or_404(queryset, residence=residence)
        serializer = RoomSerializer(list, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, residence, pk):
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=pk, residence=residence)
        serializer = RoomSerializer(user, context={'request': request})
        return Response(serializer.data)