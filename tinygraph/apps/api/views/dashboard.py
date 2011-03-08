from tinygraph.apps.api.utils import CsrfBaseHandler
from tinygraph.apps.dashboard.models import Board, Item, Connection
from piston.utils import rc

class BoardHandler(CsrfBaseHandler):
    model = Board

class ItemHandler(CsrfBaseHandler):
    model = Item
    
    def _resolve_board(self, request):
        post_dct = request.data.copy()
        if 'board' in post_dct:
            try:
                post_dct['board'] = Board.objects.get(pk=post_dct['board'])
            except Board.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('Board with primary key "%d" not found.' % dct['board'])
                return resp
        request.data = post_dct
        return None
    
    def create(self, request):
        resp = self._resolve_board(request)
        if resp is not None:
            return resp
        print request.POST
        return super(ItemHandler, self).create(request)
    
    def update(self, request, *args, **kwargs):
        resp = self._resolve_board(request)
        if resp is not None:
            return resp
        return super(ItemHandler, self).update(request, *args, **kwargs)

class ConnectionHandler(CsrfBaseHandler):
    model = Connection
    