from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.rules import RuleHandler, PackageInstanceHandler

rule_handler = Resource(RuleHandler)
package_instance_handler = Resource(PackageInstanceHandler)

urlpatterns = patterns('',
    url(r'^rule/$', rule_handler, name='rules'),
    url(r'^rule/(?P<id>\d+)/$', rule_handler, name='rule'),
    
    url(r'^package-instance/$', package_instance_handler, name='package_instances'),
    url(r'^package-instance/(?P<id>\d+)/$', package_instance_handler, name='package_instance'),
)