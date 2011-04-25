from django.conf.urls.defaults import *
from tinygraph.apps.rules.views import package_instance_detail, package_instance_membership_detail

urlpatterns = patterns('devices.views',
    url(r'^add/$', 'device_add', name='device_add'),
    url(r'^test/$', 'test', name='test'),
    url(r'^(?P<device_slug>[-\w]+)/$', 'device_detail', name='device_detail'),
    url(r'^(?P<device_slug>[-\w]+)/data-objects/$', 'device_data_object_list', name='device_data_object_list'),
    url(r'^(?P<device_slug>[-\w]+)/delete/$', 'device_delete', name='device_delete'),
    url(r'^(?P<device_slug>[-\w]+)/edit/$', 'device_edit', name='device_edit'),
    url(r'^(?P<device_slug>[-\w]+)/(?P<package_slug>[-\w]+)/$', package_instance_detail, name='package_instance_detail'),
    url(r'^(?P<device_slug>[-\w]+)/(?P<package_slug>[-\w]+)/(?P<data_object_derived_name>[^/]+)/(?P<suffix>[^/]+)/$', package_instance_membership_detail, name='package_instance_membership_detail'),
    
    url(r'^$', 'device_list', name='device_list'),
)