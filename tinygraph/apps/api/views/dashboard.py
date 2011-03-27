from tinygraph.apps.api.utils import CsrfBaseHandler
from tinygraph.apps.dashboard.models import Board, Item, Connection
from tinygraph.apps.devices.models import Device
from piston.utils import rc
from django.core.exceptions import ValidationError

class BoardHandler(CsrfBaseHandler):
    model = Board

class ItemHandler(CsrfBaseHandler):
    model = Item
    
    def _resolve_fks(self, request):
        dct = request.data.copy()
        
        # Replaces the board fk with an actual reference
        if 'board' in dct:
            try:
                dct['board'] = Board.objects.get(pk=dct['board'])
            except Board.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('Board with primary key "%d" not found.' % dct['board'])
                return resp
        
        # Replaces the devices fk with an actual reference
        if  'device' in dct:
            try:
                dct['device'] = Device.objects.get(pk=dct['device'])
            except Device.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('Device with primary key "%d" not found.' % dct['device'])
                return resp
        request.data = dct
        return None
    
    def create(self, request):
        resp = self._resolve_fks(request)
        if resp is not None:
            return resp
        return super(ItemHandler, self).create(request)
    
    def update(self, request, *args, **kwargs):
        resp = self._resolve_fks(request)
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
        try:
            return super(ConnectionHandler, self).create(request, *args, **kwargs)
        except ValidationError, e:
            resp = rc.BAD_REQUEST
            resp.write(str(e))
            return resp

    def update(self, request, *args, **kwargs):
        resp = self._resolve_devices(request)
        if resp is not None:
            return resp
        try:
            return super(ConnectionHandler, self).update(request, *args, **kwargs)
        except ValidationError, e:
            resp = rc.BAD_REQUEST
            resp.write(str(e))
            return resp