from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.rules import RuleHandler, PackageInstanceHandler, \
    PackageInstanceMembershipHandler

rule_handler = Resource(RuleHandler)
package_instance_handler = Resource(PackageInstanceHandler)
package_instance_membership_handler = Resource(PackageInstanceMembershipHandler)

urlpatterns = patterns('',
    url(r'^rule/$', rule_handler, name='rules'),
    url(r'^rule/(?P<id>\d+)/$', rule_handler, name='rule'),
    
    url(r'^package-instance/$', package_instance_handler, name='package_instances'),
    url(r'^package-instance/(?P<id>\d+)/$', package_instance_handler, name='package_instance'),
    
    url(r'^package-instance-membership/$', package_instance_membership_handler, name='package_instance_memberships'),
    url(r'^package-instance-membership/(?P<id>\d+)/$', package_instance_membership_handler, name='package_instance_membership'),
)