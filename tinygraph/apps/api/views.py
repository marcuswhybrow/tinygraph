from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template
from django.http import Http404, HttpResponse
from core.models import DataObject
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

def analyse(request):
    if request.is_ajax() and request.method == 'POST' and 'device_pk' in request.POST:
        device_pk = request.POST['device_pk']
        try:
            Device.objects.get(pk=device_pk)
        except Device.DoesNotExist:
            data = {'success': False}
        else:
            data = {'success': True}

def data_object_children_list(request):
    if request.is_ajax() and request.method == 'POST' and 'data_object_pk' in request.POST:
        data_object_pk = request.POST['data_object_pk']
        return direct_to_template(request, 'core/includes/data_object_children_list.html', {
            'data_object_children': DataObject.objects.filter(parent__pk=data_object_pk),
        })
    raise Http404