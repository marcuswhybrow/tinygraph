from tinygraph.apps.api.utils import ImprovedHandler
from tinygraph.apps.dashboard.models import Board, Item, Connection, \
    DeviceItem
from tinygraph.apps.devices.models import Device
from piston.utils import rc
from django.core.exceptions import ValidationError

class BoardHandler(ImprovedHandler):
    model = Board

class ItemHandler(ImprovedHandler):
    model = Item

class DeviceItemHandler(ImprovedHandler):
    model = DeviceItem

class ConnectionHandler(ImprovedHandler):
    model = Connection