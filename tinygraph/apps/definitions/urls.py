from django.conf.urls.defaults import *
from django.views.generic.edit import CreateView
from tinygraph.apps.definitions.models import Package

urlpatterns = patterns('definitions.views',
    url(r'^mibs/$', 'mib_upload_list', name='mib_upload_list'),
    
    url(r'^packages/$', 'package_list', name='package_list'),
    url(r'^packages/add/$', CreateView.as_view(model=Package, template_name='definitions/packages/package_form.html'), name='package_add'),
    url(r'^packages/(?P<package_slug>[-\w]+)/$', 'package_detail', name='package_detail'),

    url(r'^$', 'data_object_list', name='data_object_list'),
)