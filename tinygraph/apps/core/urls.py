from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',
    (r'^devices/$', 'device_list'),
    (r'^devices/add/$', 'device_add'),
    (r'^devices/(?P<device_slug>[-\w]+)/$', 'device_detail'),
    (r'^devices/(?P<device_slug>[-\w]+)/data-objects/$', 'device_data_object_list'),
    (r'^devices/(?P<device_slug>[-\w]+)/delete/$', 'device_delete'),
    (r'^devices/(?P<device_slug>[-\w]+)/edit/$', 'device_edit'),
    
    (r'^data-objects/$', 'data_object_list'),
    (r'^data-objects/mibs/$', 'mib_upload_list'),
    
    (r'^packages/$', 'package_list'),
    (r'^packages/(?P<package_slug>[-\w]+)/$', 'package_detail'),
    
    (r'^$', 'index'),
)