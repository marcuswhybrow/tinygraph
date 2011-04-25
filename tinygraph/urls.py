from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )

urlpatterns += patterns('',
    (r'^api/', include('api.urls.urls', namespace='api')),
    (r'^devices/', include('devices.urls', namespace='devices')),
    (r'^data/', include('definitions.urls', namespace='definitions')),
    
    url(r'^settings/', 'tinygraph.apps.core.views.settings', name='settings'),
    
    url(r'^', include('dashboard.urls', namespace='dashboard')),
)