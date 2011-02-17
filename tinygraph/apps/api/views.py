from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template
from django.http import Http404, HttpResponse
from definitions.models import DataObject
from dashboard.models import Item, Board
import simplejson
import subprocess

def ping(request):
    if request.is_ajax() and request.method == 'POST':
        address = request.POST.get('address')
        address = address.split(' ')[0]
        sequence = request.POST.get('sequence')
        timeout = request.POST.get('timeout', 3000)
        if address is not None and sequence is not None:
            result = subprocess.call(['ping', '-c 1', '-W %s' % timeout, address])
            data = {
                'up': True if result == 0 else False,
                'sequence': sequence,
                'address': address,
            }
            
            return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    raise Http404

def data_object_children_list(request):
    if request.is_ajax() and request.method == 'POST' and 'data_object_pk' in request.POST:
        data_object_pk = request.POST['data_object_pk']
        return direct_to_template(request, 'definitions/includes/data_object_children_list.html', {
            'data_object_children': DataObject.objects.filter(parent__pk=data_object_pk),
        })
    raise Http404

def dashboard_create_item(request):
    if request.method == 'POST':# and all(name in request.POST for name in ['item_x', 'item_y', 'item_type', 'item_board_pk']):
        x = request.POST['item_x']
        y = request.POST['item_y']
        type = request.POST['item_type']
        board_pk = request.POST['item_board_pk']
        
        device_pk = request.POST.get('item_device_pk')
        
        board = Board.objects.get(pk=board_pk)
        
        fields = {
            'x': x,
            'y': y,
            'type': type,
            'board': board,
        }
        
        if device_pk is not None:
            fields['device'] = device_pk
        
        Item.objects.create(**fields)
        data = {'created': True}
    else:
        data = {'incorrect-arguments': True}
        
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    