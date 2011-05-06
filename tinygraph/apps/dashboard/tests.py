from django.test import TestCase
from django.core.exceptions import ValidationError
from tinygraph.apps.dashboard.models import Board, DeviceItem, Connection
from tinygraph.apps.devices.models import Device

class IntegrityTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='The Default Board')
        
        self.device_one = Device.objects.create(user_given_name='Device One',
            user_given_address='deviceoneaddress', snmp_version='2')
        self.device_two = Device.objects.create(user_given_name='Device Two',
            user_given_address='devicetwoaddress', snmp_version='2')
            
        self.device_item_one = DeviceItem.objects.create(board=self.board,
            device=self.device_one, x=1, y=1)
        self.device_item_two = DeviceItem.objects.create(board=self.board,
            device=self.device_two, x=2, y=2)
    
    def test_connection_creation(self):
        connection = Connection.objects.create(from_item=self.device_item_one,
            to_item=self.device_item_two)
    
    def test_for_error_when_the_same_device_the_other_way(self):
        """
        This should fail becure a connection already exists from
        device_item_one to device_item_two
        """
        Connection.objects.create(from_item=self.device_item_one,
            to_item=self.device_item_two)
        try:
            Connection.objects.create(from_item=self.device_item_two,
                to_item=self.device_item_one)
        except ValidationError:
            pass
        else:
            assert False, 'No validation error was raised'
    
    def test_for_error_when_connecting_the_same_device(self):
        try:
            Connection.objects.create(from_item=self.device_item_one,
                to_item=self.device_item_one)
        except ValidationError:
            pass
        else:
            assert False, 'No validation error was raised'