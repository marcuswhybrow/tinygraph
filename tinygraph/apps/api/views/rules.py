from piston.handler import BaseHandler
from tinygraph.apps.rules.models import Rule, PackageInstance, \
    PackageInstanceMembership
from tinygraph.apps.devices.models import Device
from tinygraph.apps.definitions.models import Package

class RuleHandler(BaseHandler):
    model = Rule

class PackageInstanceHandler(BaseHandler):
    model = PackageInstance

class PackageInstanceMembershipHandler(BaseHandler):
    model = PackageInstanceMembership