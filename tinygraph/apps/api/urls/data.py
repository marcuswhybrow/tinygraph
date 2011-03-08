from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.data import DataInstanceHandler

data_instance_handler = Resource(DataInstanceHandler)

urlpatterns = patterns('',
    url(r'^data-instance/$', data_instance_handler, name='data_instances'),
    url(r'^data-instance/(?P<id>\d+)/$', data_instance_handler, name='data_instance'),
)