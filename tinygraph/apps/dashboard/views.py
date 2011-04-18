from django.views.generic.simple import direct_to_template
from tinygraph.apps.dashboard.models import Board, Item, Connection
from tinygraph.apps.devices.models import Device
from django.db.models import Count

def index(request):
    # For now assum the first Board in the database is the one to display
    try:
        board = Board.objects.get(pk=1)
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
    
    device_counts = Item.objects.filter(board=board).values('device').annotate(count=Count('device'))
    
    device_list = []
    for device in devices:
        placed = False
        for item in device_counts:
            if item['device'] == device.pk:
                placed = item['count'] > 0
                break
        device_list.append((device, placed))
    
    return direct_to_template(request, 'dashboard/index.html', {
        'board': board,
        'items': items,
        'connections': connections,
        'devices': device_list,
    })
