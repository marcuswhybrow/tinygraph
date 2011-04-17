from tinygraph.apps.api.utils import ImprovedHandler
from tinygraph.apps.dashboard.models import Board, Item, Connection
from tinygraph.apps.devices.models import Device
from piston.utils import rc
from django.core.exceptions import ValidationError

class BoardHandler(ImprovedHandler):
    model = Board

class ItemHandler(ImprovedHandler):
    model = Item

class ConnectionHandler(ImprovedHandler):
    model = Connection