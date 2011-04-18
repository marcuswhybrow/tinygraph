from django.conf.urls.defaults import *

urlpatterns = patterns('api.views.core',
    url(r'^ping/$', 'ping', name='ping'),
    url(r'^data-object-children-list/$', 'data_object_children_list', name='data_object_children_list'),
    url(r'^dashboard-create-item/$', 'dashboard_create_item', name='dashboard_create_item'),
    url(r'^lookup-data-object-name/$', 'lookup_data_object_name', name='lookup_data_object_name'),
)