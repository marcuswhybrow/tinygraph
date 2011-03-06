from django.conf.urls.defaults import *

urlpatterns = patterns('definitions.views',
    url(r'^mibs/$', 'mib_upload_list', name='mib_upload_list'),
    
    url(r'^packages/$', 'package_list', name='package_list'),
    url(r'^packages/(?P<package_slug>[-\w]+)/$', 'package_detail', name='package_detail'),

    url(r'^$', 'data_object_list', name='data_object_list'),
)