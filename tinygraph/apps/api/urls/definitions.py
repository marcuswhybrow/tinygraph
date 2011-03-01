from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.definitions import DataObjectHandler, PackageHandler, MibUploadHandler

data_object_handler = Resource(DataObjectHandler)
package_handler = Resource(PackageHandler)
mib_upload_handler = Resource(MibUploadHandler)

urlpatterns = patterns('',
    # (r'^data-object/$', data_object_handler),
    (r'^data-object/(?P<id>\d+)/$', data_object_handler),
    
    (r'^package/$', package_handler),
    (r'^package/(?P<id>\d+)/$', package_handler),
)