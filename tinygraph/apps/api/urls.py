from django.conf.urls.defaults import *

urlpatterns = patterns('api.views',
    (r'^ping/$', 'ping'),
    (r'^data-object-children-list/$', 'data_object_children_list'),
    (r'^dashboard-create-item/$', 'dashboard_create_item'),
)