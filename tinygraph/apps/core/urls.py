from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',
    
    (r'^data-objects/$', 'data_object_list'),
    (r'^data-objects/mibs/$', 'mib_upload_list'),
    
    (r'^packages/$', 'package_list'),
    (r'^packages/(?P<package_slug>[-\w]+)/$', 'package_detail'),
    
    (r'^$', 'index'),
)