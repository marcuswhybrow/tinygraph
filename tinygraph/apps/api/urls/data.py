from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.data import DataInstanceHandler

data_instance_handler = Resource(DataInstanceHandler)

urlpatterns = patterns('',
    # (r'^data-instance/$', data_instance_handler),
    (r'^data-instance/(?P<id>\d+)/$', data_instance_handler),
)