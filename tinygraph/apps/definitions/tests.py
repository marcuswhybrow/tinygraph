from django.test import TestCase
from tinygraph.apps.definitions.models import Package, DataObject, \
    PackageMembership
from tinygraph.apps.devices.models import Device
from tinygraph.apps.rules.models import PackageInstance, \
    PackageInstanceMembership

class IntegrityTests(TestCase):
    def setUp(self):
        # Create an existing device
        self.device = Device.objects.create(user_given_name='newDevice',
            user_given_address='newdevice', snmp_version='2')
        
        # Create the new Package
        self.package = Package.objects.create(title='New Package')
        
        # Create an imaginary data object
        self.data_object = DataObject.objects.create(identifier='1')
        
        # Put that data object in the package
        self.package_membership = PackageMembership.objects.create(
            package=self.package, data_object=self.data_object)
        
    def test_package_instance_creation(self):
        """
        Test that exactly one PackageInstance exists for the existing
        device and this new Package
        """
        num = PackageInstance.objects.filter(device=self.device,
            package=self.package).count()
        
        self.assertEqual(num, 1)
    
    def test_package_instance_membership_creation(self):
        """
        Test that for the new PackageMemebership, a PackageInstanceMembership
        exists
        """
        
        package_instance = PackageInstance.objects.get(device=self.device,
            package=self.package)
        
        num = PackageInstanceMembership.objects.filter(
            package_instance=package_instance,
            package_membership=self.package_membership).count()
        
        self.assertEqual(num, 1)