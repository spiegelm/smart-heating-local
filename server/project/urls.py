from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

#from rest_framework import routers
#from snippets import views
#
#router = routers.DefaultRouter()
#router.register(r'snippets', views.SnippetViewSet)
#
## Wire up our API using automatic URL routing.
## Additionally, we include login URLs for the browsable API.
#urlpatterns = [
#    url(r'^', include(router.urls)),
#    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
#]

urlpatterns = [
    url(r'^', include('smart_heating.urls')),
]

