from django.conf.urls.defaults import *

urlpatterns = patterns('devices.views',
    (r'^add/$', 'device_add'),
    (r'^(?P<device_slug>[-\w]+)/$', 'device_detail'),
    (r'^(?P<device_slug>[-\w]+)/data-objects/$', 'device_data_object_list'),
    (r'^(?P<device_slug>[-\w]+)/delete/$', 'device_delete'),
    (r'^(?P<device_slug>[-\w]+)/edit/$', 'device_edit'),
    
    (r'^test/$', 'test'),
    
    (r'^$', 'device_list'),
)