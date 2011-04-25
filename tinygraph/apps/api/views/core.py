from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template
from django.http import Http404, HttpResponse
from tinygraph.apps.definitions.models import DataObject
from tinygraph.apps.dashboard.models import Item, Board
from django.core.cache import cache
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

def lookup_data_object_name(request):
    data = {}
    if request.is_ajax() and request.method == 'POST':
        user_input = request.POST.get('user_input')
        request_id = request.POST.get('request_id')
        
        parent = None
        derived_name = user_input
        
        while derived_name != '':
            try:
                parent = DataObject.objects.get(derived_name=derived_name)
            except DataObject.DoesNotExist:
                derived_name = '.'.join(derived_name.split('.')[:-1])
                continue
            else:
                break
        
        matches = DataObject.objects.filter(derived_name__startswith=user_input, parent=parent).values('pk', 'identifier', 'derived_name')
        
        data['user_input'] = user_input
        data['user_input_data_object'] = {
            'pk': parent.pk,
            'derived_name': parent.derived_name,
            'identifier': parent.identifier,
        } if parent and derived_name == user_input else None
        data['request_id'] = request_id
        data['data_objects'] = list(matches)
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')

def reset_caches(request):
    if request.is_ajax() and request.method == 'POST':
        cache.clear()
        return HttpResponse()
    raise Http404