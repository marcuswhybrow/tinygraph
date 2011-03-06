from django.conf.urls.defaults import *

urlpatterns = patterns('devices.views',
    url(r'^add/$', 'device_add', name='device_add'),
    url(r'^test/$', 'test', name='test'),
    url(r'^d/(?P<device_slug>[-\w]+)/$', 'device_detail', name='device_detail'),
    url(r'^d/(?P<device_slug>[-\w]+)/data-objects/$', 'device_data_object_list', name='device_data_object_list'),
    url(r'^d/(?P<device_slug>[-\w]+)/delete/$', 'device_delete', name='device_delete'),
    url(r'^d/(?P<device_slug>[-\w]+)/edit/$', 'device_edit', name='device_edit'),
    
    url(r'^$', 'device_list', name='device_list'),
)