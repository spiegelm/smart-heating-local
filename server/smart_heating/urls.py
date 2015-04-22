from django.conf.urls import url
from smart_heating import views

urlpatterns = [
    url(r'^residence/$', views.residence_list),
    url(r'^residence/1/thermostats/$', views.thermostat_list),
#    url(r'^buildings/1/thermostats/(?P<rfid>[0-9a-f]+)/$', views.snippet_detail),
]

