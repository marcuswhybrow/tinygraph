from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',
    (r'^devices/$', 'device_list'),
    (r'^devices/add/$', 'device_edit'),
    (r'^devices/(?P<device_slug>[^/]+)/$', 'device_detail'),
    (r'^devices/(?P<device_slug>[^/]+)/delete/$', 'device_delete'),
    (r'^devices/(?P<device_slug>[^/]+)/edit/$', 'device_edit'),
    
    (r'^protocols/$', 'protocol_list'),
    (r'^protocols/(?P<protocol_slug>[^/]+)/$', 'protocol_detail'),
    (r'^protocols/(?P<protocol_slug>[^/]+)/(?P<protocol_version_slug>[^/]+)/$', 'protocol_version_detail'),
)