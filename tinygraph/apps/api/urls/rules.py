from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.rules import RuleHandler, PackageInstanceHandler

rule_handler = Resource(RuleHandler)
package_instance_handler = Resource(PackageInstanceHandler)

urlpatterns = patterns('',
    (r'^rule/$', rule_handler),
    (r'^rule/(?P<id>\d+)/$', rule_handler),
    
    (r'^package-instance/$', package_instance_handler),
    (r'^package-instance/(?P<id>\d+)/$', package_instance_handler),
)