from django.views.generic.simple import direct_to_template
from dashboard.models import Board, Item, Connection
from devices.models import Device

def index(request):
    # For now assum the first Board in the database is the one to display
    try:
        board = Board.objects.get(pk=2)
    except Board.DoesNotExist:
        board = None
    
    items = []
    connections = []
    
    # If the board this page is displaying exists, then get its items and
    # conntections. It is far more efficient to do the queries here, than
    # in the template later on.
    if board is not None:
        items = Item.objects.filter(board=board)
        connections = Connection.objects.select_related().filter(from_item__board=board)
    
    # All of the devices in the system
    devices = Device.objects.select_related()
    
    return direct_to_template(request, 'dashboard/index.html', {
        'board': board,
        'items': items,
        'connections': connections,
        'devices': devices,
    })