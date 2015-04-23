from django.conf.urls import url, include
from rest_framework import routers
from smart_heating import views

router = routers.DefaultRouter()
router.register(r'residence', views.ResidenceViewSet)
router.register(r'room', views.RoomViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
]

