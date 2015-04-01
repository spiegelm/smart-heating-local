from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from smart_heating.models import Thermostat
from smart_heating.serializers import ThermostatSerializer

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def thermostat_list(request):
    """
    List all code snippets
    """
    if request.method == 'GET':
        thermostats = Thermostat.objects.all()
        serializer = ThermostatSerializer(thermostats, many=True)
        return JSONResponse(serializer.data)



