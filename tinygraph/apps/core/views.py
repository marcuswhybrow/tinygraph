from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from core.models import Device, DataObject, MibUpload, Package, DataInstance
from core.forms import DeviceForm, MibUploadForm
from django.conf import settings
from core.presenters import Presenter, CounterPresenter

import datetime
import urllib

def device_list(request):
    return direct_to_template(request, 'core/device/device_list.html', {
        'devices': Device.objects.all(),
    })

def device_detail(request, device_slug):
    device = get_object_or_404(Device, slug=device_slug)
            
    return direct_to_template(request, 'core/device/device_detail.html', {
        'device': device,
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
    
    return direct_to_template(request, 'core/device/device_edit.html', {
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
    
    return direct_to_template(request, 'core/device/device_delete.html', {
        'device': device,
        'deleted': deleted,
    })
        
def index(request):
    # It's simple now but will probably require expantion
    return direct_to_template(request, 'core/index.html', {})

def data_object_list(request):
    return direct_to_template(request, 'core/data_object/data_object_list.html', {
        'root_data_object_list': DataObject.objects.root_only().select_related(),
    })

def mib_upload_list(request):
    if request.method == 'POST':
        form = MibUploadForm(request.POST, request.FILES)
        if form.is_valid():
            mib_upload = form.save()
            return direct_to_template(request, 'core/data_object/mib_upload_uploaded.html', {
                'mib_upload': mib_upload,
            })
    else:
        form = MibUploadForm()
    
    return direct_to_template(request, 'core/data_object/mib_upload_list.html', {
        'mib_uploads': MibUpload.objects.filter(system=False),
        'form': form,
    })

def device_add(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            return HttpResponseRedirect('%s?new' % reverse('core.views.device_data_object_list', kwargs={
                'device_slug': device.slug,
            }))
    else:
        form = DeviceForm()
    
    return direct_to_template(request, 'core/device/device_add.html', {
        'form': form
    })

def device_data_object_list(request, device_slug):
    device = get_object_or_404(Device, slug=device_slug)
    return direct_to_template(request, 'core/device/device_data_object_list.html', {
        'device': device,
        'new_device': 'new' in request.GET and request.GET['new'].lower() in ['', 'true'],
        'packages': Package.objects.all().select_related('devices'),
    })

def package_list(request):
    return direct_to_template(request, 'core/package/package_list.html', {
        'custom_packages': Package.objects.filter(editable=True),
        'system_packages': Package.objects.filter(editable=False),
    })

def package_detail(request, package_slug):
    package = get_object_or_404(Package, slug=package_slug)
    return direct_to_template(request, 'core/package/package_detail.html', {
        'package': package,
    })

def test(request):
    # Some device
    device = get_object_or_404(Device, pk=1)
    # ...11 = ifInUcastPkts, ...16 = ifOutOctets
    oid = '1.3.6.1.2.1.2.2.1.11'
    # vHost's 3rd interface (not the loopback - 1, or the other NIC - 2)
    suffix = '3'
    # 10 minutes ago
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=10)
    # Get the data instances
    data_instances = DataInstance.objects.filter(data_object__identifier=oid, rule__device=device, suffix=suffix, created__gte=cutoff)
    
    # Return the data instances in a presentor
    return direct_to_template(request, 'core/test.html', {
        'data_instances': CounterPresenter(data_instances),
    })