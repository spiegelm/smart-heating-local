from django.conf.urls import url, include
from rest_framework import routers
from smart_heating import views


router = routers.DefaultRouter()
router.register(r'residence', views.ResidenceViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    # url(r'^residence/$', views.residence_list),
    url(r'^residence/1/thermostats/$', views.thermostat_list),
    # url(r'^buildings/1/thermostats/(?P<rfid>[0-9a-f]+)/$', views.snippet_detail),
]

