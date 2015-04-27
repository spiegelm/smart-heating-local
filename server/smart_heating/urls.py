from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from smart_heating import views

router = routers.DefaultRouter()
router.register(r'residence', views.ResidenceViewSet)
# router.register(r'residence/(?P<residence_pk>[^/.]+)/room', views.RoomViewSet)
# router.register(r'residence/(?P<residence_pk>[^/.]+)/room/(?P<room_pk>[^/.]+)/thermostat', views.ThermostatViewSet)

# router = nested_routers.SimpleRouter()
# router.register(r'residence', views.ResidenceViewSet)

room_router = nested_routers.NestedSimpleRouter(router, r'residence', lookup='residence')
room_router.register(r'room', views.RoomViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(room_router.urls)),
]

