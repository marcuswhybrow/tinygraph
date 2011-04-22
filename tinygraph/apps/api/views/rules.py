from tinygraph.apps.api.utils import ImprovedHandler
from tinygraph.apps.rules.models import Rule, PackageInstance, \
    PackageInstanceMembership
from tinygraph.apps.devices.models import Device
from tinygraph.apps.definitions.models import Package

class RuleHandler(ImprovedHandler):
    model = Rule

class PackageInstanceHandler(ImprovedHandler):
    model = PackageInstance

class PackageInstanceMembershipHandler(ImprovedHandler):
    model = PackageInstanceMembership