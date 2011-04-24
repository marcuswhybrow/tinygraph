from piston.handler import BaseHandler
from tinygraph.apps.dashboard.models import Board, Item, Connection, \
    DeviceItem
from tinygraph.apps.devices.models import Device
from piston.utils import rc
from django.core.exceptions import ValidationError

class BoardHandler(BaseHandler):
    model = Board

class ItemHandler(BaseHandler):
    model = Item

class DeviceItemHandler(BaseHandler):
    model = DeviceItem

class ConnectionHandler(BaseHandler):
    model = Connection