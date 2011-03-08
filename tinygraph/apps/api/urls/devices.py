from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.devices import DeviceHandler

device_handler = Resource(DeviceHandler)

urlpatterns = patterns('',
    url(r'^device/$', device_handler, name='devices'),
    url(r'^device/(?P<id>\d+)/$', device_handler, name='device'),
)