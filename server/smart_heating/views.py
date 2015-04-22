from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from smart_heating.models import *
from smart_heating.serializers import *

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
    List all
    """
    if request.method == 'GET':
        thermostats = Thermostat.objects.all()
        serializer = ThermostatSerializer(thermostats, many=True)
        return JSONResponse(serializer.data)


@csrf_exempt
def residence_list(request):
    """
    List all
    """
    if request.method == 'GET':
        residences = Residence.objects.all()
        serializer = ResidenceSerializer(residences, many=True)
        #thermostats = Thermostat.objects.all()
        #serializer = ThermostatSerializer(thermostats, many=True)
        return JSONResponse(serializer.data)


#
# @csrf_exempt
# def snippet_detail(request, pk):
#     """
#     Retrieve, update or delete a code snippet.
#     """
#     try:
#         snippet = Snippet.objects.get(pk=pk)
#     except Snippet.DoesNotExist:
#         return HttpResponse(status=404)
#
#     if request.method == 'GET':
#         serializer = SnippetSerializer(snippet)
#         return JSONResponse(serializer.data)
#
#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = SnippetSerializer(snippet, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JSONResponse(serializer.data)
#         return JSONResponse(serializer.errors, status=400)
#
#     elif request.method == 'DELETE':
#         snippet.delete()
#         return HttpResponse(status=204)
#
#


