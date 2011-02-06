from django.conf.urls.defaults import *

urlpatterns = patterns('api.views',
    (r'^ping/$', 'ping'),
    (r'^data-object-children-list/$', 'data_object_children_list'),
    (r'^analyse/$', 'analyse'),
)