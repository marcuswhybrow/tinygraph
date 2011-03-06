from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^core/', include('api.urls.core', namespace='core')),
    (r'^devices/', include('api.urls.devices', namespace='devices')),
    (r'^dashboard/', include('api.urls.dashboard', namespace='dashboard')),
    (r'^data/', include('api.urls.data', namespace='data')),
    (r'^definitions/', include('api.urls.definitions', namespace='definitions')),
    (r'^rules/', include('api.urls.rules', namespace='rules')),
)