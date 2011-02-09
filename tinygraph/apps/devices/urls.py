from django.conf.urls.defaults import *

urlpatterns = patterns('devices.views',
    (r'^add/$', 'device_add'),
    (r'^test/$', 'test'),
    (r'^d/(?P<device_slug>[-\w]+)/$', 'device_detail'),
    (r'^d/(?P<device_slug>[-\w]+)/data-objects/$', 'device_data_object_list'),
    (r'^d/(?P<device_slug>[-\w]+)/delete/$', 'device_delete'),
    (r'^d/(?P<device_slug>[-\w]+)/edit/$', 'device_edit'),
    
    (r'^$', 'device_list'),
)