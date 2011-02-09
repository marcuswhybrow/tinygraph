from django.conf.urls.defaults import *

urlpatterns = patterns('definitions.views',
    (r'^mibs/$', 'mib_upload_list'),
    
    (r'^packages/$', 'package_list'),
    (r'^packages/(?P<package_slug>[-\w]+)/$', 'package_detail'),

    (r'^$', 'data_object_list'),
)