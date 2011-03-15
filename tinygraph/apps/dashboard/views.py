from django.views.generic.simple import direct_to_template
from dashboard.models import Board, Item, Connection

def index(request):
    try:
        board = Board.objects.get(pk=1)
    except Board.DoesNotExist:
        board = None
    
    items = []
    connections = []
    
    if board is not None:
        items = Item.objects.filter(board=board)
        connections = Connection.objects.select_related().filter(from_item__board=board)
    
    return direct_to_template(request, 'dashboard/index.html', {
        'board': board,
        'items': items,
        'connections': connections,
    })