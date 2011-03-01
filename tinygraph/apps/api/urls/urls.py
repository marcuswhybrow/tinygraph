from django.conf.urls.defaults import *

urlpatterns = patterns('api.views',
    (r'^core/', include('api.urls.core')),
    (r'^devices/', include('api.urls.devices')),
    (r'^dashboard/', include('api.urls.dashboard')),
    (r'^data/', include('api.urls.data')),
    (r'^definitions/', include('api.urls.definitions')),
    (r'^rules/', include('api.urls.rules')),
)