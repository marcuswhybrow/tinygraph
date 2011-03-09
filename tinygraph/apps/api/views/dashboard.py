from tinygraph.apps.api.utils import CsrfBaseHandler
from tinygraph.apps.dashboard.models import Board, Item, Connection
from piston.utils import rc

class BoardHandler(CsrfBaseHandler):
    model = Board

class ItemHandler(CsrfBaseHandler):
    model = Item
    
    def _resolve_board(self, request):
        dct = request.data.copy()
        if 'board' in dct:
            try:
                dct['board'] = Board.objects.get(pk=dct['board'])
            except Board.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('Board with primary key "%d" not found.' % dct['board'])
                return resp
        request.data = dct
        return None
    
    def create(self, request):
        resp = self._resolve_board(request)
        if resp is not None:
            return resp
        return super(ItemHandler, self).create(request)
    
    def update(self, request, *args, **kwargs):
        resp = self._resolve_board(request)
        if resp is not None:
            return resp
        return super(ItemHandler, self).update(request, *args, **kwargs)

class ConnectionHandler(CsrfBaseHandler):
    model = Connection
    
    def _resolve_devices(self, request):
        dct = request.data.copy()
        if 'from_item' in dct:
            try:
                dct['from_item'] = Item.objects.get(pk=dct['from_item'])
            except Board.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('Item with primary key "%d" not found.' % dct['from_item'])
                return resp
        if 'to_item' in dct:
            try:
                dct['to_item'] = Item.objects.get(pk=dct['to_item'])
            except Board.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('Item with primary key "%d" not found.' % dct['to_item'])
                return resp
        request.data = dct
        return None
    
    def create(self, request, *args, **kwargs):
        resp = self._resolve_devices(request)
        if resp is not None:
            return resp
        return super(ConnectionHandler, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        resp = self._resolve_devices(request)
        if resp is not None:
            return resp
        return super(ConnectionHandler, self).update(request, *args, **kwargs)