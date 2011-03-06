from django.conf.urls.defaults import *

urlpatterns = patterns('dashboard.views',
    url(r'^$', 'index', name='index'),
)