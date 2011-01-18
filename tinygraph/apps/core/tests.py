from django.test import TestCase
from tinygraph.apps.core.models import Device, Protocol

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

class ProtocolTest(TestCase):
    def test_unicode_name(self):
        """
        Tests that a Protocol displays its name correctly based upon the data
        it has available
        """
        
        protocol = Protocol(acronym='SNMP')
        self.failUnlessEqual(str(protocol), 'SNMP')
        
        protocol.version = '2c'
        self.failUnlessEqual(str(protocol), 'SNMPv2c')
        
        # Should still produce the same result as the previous test
        protocol.name = 'Simple Network Management Protocol'
        self.failUnlessEqual(str(protocol), 'SNMPv2c')