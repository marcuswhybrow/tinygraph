from django.conf.urls.defaults import *

urlpatterns = patterns('tinygraph.apps.core.views',
    (r'^devices/$', 'device_list'),
    (r'^protocols/$', 'protocol_list'),
    (r'^protocols/(?P<protocol_slug>[^/]+)/$', 'protocol_detail'),
    (r'^protocols/(?P<protocol_slug>[^/]+)/(?P<protocol_version_slug>[^/]+)/$', 'protocol_version_detail'),
)