from django.test import TestCase
from tinygraph.apps.devices.models import Device

class UsabilityTests(TestCase):
    def test_device_creation_requirements(self):
        """
        Checks that a device can be created by specifying only a name, address
        and snmp version.
        """
        device = Device.objects.create(
            user_given_name='Devce name',
            user_given_address='devicefqdn',
            snmp_version='2')
        
        assert device.pk is not None, 'Device could not be created'