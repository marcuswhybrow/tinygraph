from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',
    (r'^devices/$', 'device_list'),
    (r'^devices/add/$', 'device_add'),
    (r'^devices/(?P<device_slug>[^/]+)/$', 'device_detail'),
    (r'^devices/(?P<device_slug>[^/]+)/data-objects/$', 'device_data_object_list'),
    (r'^devices/(?P<device_slug>[^/]+)/delete/$', 'device_delete'),
    (r'^devices/(?P<device_slug>[^/]+)/edit/$', 'device_edit'),
    
    (r'^data-objects/$', 'data_object_list'),
    (r'^data-objects/mibs/$', 'mib_upload_list'),
    
    (r'^$', 'index'),
)