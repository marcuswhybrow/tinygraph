from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from core.models import Device, DataObject
from core.forms import DeviceForm
import subprocess
import simplejson

def device_list(request):
    return direct_to_template(request, 'core/device_list.html', {
        'devices': Device.objects.all(),
    })

def device_detail(request, device_slug):
    return direct_to_template(request, 'core/device_detail.html', {
        'device': get_object_or_404(Device, slug=device_slug),
    })

def device_edit(request, device_slug=None):
    device = None
    if device_slug is not None:
        device = get_object_or_404(Device, slug=device_slug)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            # Note "device" will be None if creating a new Device
            saved_device = form.save()
            return HttpResponseRedirect(reverse('core.views.device_detail', kwargs={
                'device_slug': saved_device.slug,
            }))
    else:
        form = DeviceForm(instance=device)
    
    return direct_to_template(request, 'core/device_edit.html', {
        'form': form,
    })

def device_delete(request, device_slug):
    device = get_object_or_404(Device, slug=device_slug)
    deleted = False
    
    if request.method == 'POST':
        delete = request.POST.get('delete')
        if delete is not None and delete.lower() == 'true':
            device.delete()
            deleted = True
    
    return direct_to_template(request, 'core/device_delete.html', {
        'device': device,
        'deleted': deleted,
    })

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
    if request.is_ajax() and request.method == 'POST' and 'device_pk' in request.method.POST:
        device_pk = request.POST['device_pk']
        try:
            Device.objects.get(pk=device_pk)
        except Device.DoesNotExist:
            data = {'success': False}
        else:
            data = {'success': True}
        
        