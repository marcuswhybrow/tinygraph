from django.test import TestCase
from tinygraph.apps.core.models import Device

class DeviceTest(TestCase):
    def test_unicode_name(self):
        """
        Tests that a Device displays its name correctly based upon the data
        it has available.
        """
        
        # Device has no data
        device = Device()
        self.failUnlessEqual(str(device), 'Device')
        
        # only IP address
        device.address = '172.17.10.200'
        self.failUnlessEqual(str(device), '172.17.10.200')
        
        # host name and IP address
        device.host_name = 'server.domain'
        self.failUnlessEqual(str(device),
                             'server.domain (172.17.10.200)')
        
        # only host name
        device.address = None
        self.failUnlessEqual(str(device), 'server.domain')
        
        # has a "user given name" which overrides all determined values
        device.user_given_name = 'My Server'
        self.failUnlessEqual(str(device), 'My Server')