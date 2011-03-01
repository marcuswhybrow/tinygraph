from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.devices import DeviceHandler

device_handler = Resource(DeviceHandler)

urlpatterns = patterns('',
    (r'^device/$', device_handler),
    (r'^device/(?P<id>\d+)/$', device_handler),
)