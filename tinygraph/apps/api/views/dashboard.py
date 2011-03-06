from piston.handler import BaseHandler
from tinygraph.apps.dashboard.models import Board, Item, Connection

class BoardHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Board

class ItemHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Item

class ConnectionHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Connection
    