from django.test import TestCase
from tinygraph.apps.definitions.models import Package, DataObject, \
    PackageMembership
from tinygraph.apps.devices.models import Device
from tinygraph.apps.rules.models import PackageInstance, \
    PackageInstanceMembership, PackageRule

class RuleCreationTests(TestCase):
    def setUp(self):
        self.device = Device.objects.create(user_given_name='newdevice',
            user_given_address='newdevice', snmp_version='2')
        
        self.package = Package.objects.create(title='newpackage')
        
        data_object = DataObject.objects.create(identifier='1')
        self.package_membership = PackageMembership.objects.create(
            package=self.package, data_object=data_object)
        
        package_instance = PackageInstance.objects.get(device=self.device,
            package=self.package)
        
        self.package_instance_membership = \
            PackageInstanceMembership.objects.get(
                package_membership=self.package_membership,
                package_instance=package_instance)
    
    def test_rule_creation_from_package(self):
        """
        Each device package instance membership should have a matching
        PackageRule
        """
        rule = self.package_instance_membership.rule
        
        assert isinstance(rule, PackageRule), 'PackageRule does not exist'