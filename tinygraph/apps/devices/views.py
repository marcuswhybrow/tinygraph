from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from tinygraph.apps.devices.models import Device
from tinygraph.apps.devices.forms import DeviceForm
from tinygraph.apps.definitions.models import Package
from tinygraph.apps.rules.models import PackageInstance
from tinygraph.apps.data.models import DataInstance
from tinygraph.apps.data.presenters import Presenter, CounterPresenter

import datetime

def device_list(request):
    return direct_to_template(request, 'devices/device_list.html', {
        'devices': Device.objects.all(),
    })

def device_detail(request, device_slug):
    device = get_object_or_404(Device, slug=device_slug)
    enabled_package_instances = PackageInstance.objects.filter(device=device, enabled=True)
    package_instances = [(package_instance, package_instance.memberships.filter(graphed=True).select_related()) for package_instance in enabled_package_instances]
            
    return direct_to_template(request, 'devices/device_detail.html', {
        'device': device,
        'events': device.event_set.all()[:20],
        'package_instances': package_instances,
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
            return HttpResponseRedirect(reverse('devices:device_detail', kwargs={
                'device_slug': saved_device.slug,
            }))
    else:
        form = DeviceForm(instance=device)
    
    return direct_to_template(request, 'devices/device_edit.html', {
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
    
    return direct_to_template(request, 'devices/device_delete.html', {
        'device': device,
        'deleted': deleted,
    })

def device_add(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save()
            return HttpResponseRedirect('%s?new' % reverse('devices:device_data_object_list', kwargs={
                'device_slug': device.slug,
            }))
    else:
        form = DeviceForm()

    return direct_to_template(request, 'devices/device_add.html', {
        'form': form
    })

def device_data_object_list(request, device_slug):
    device = get_object_or_404(Device, slug=device_slug)
    packages = Package.objects.all().select_related('devices')
    packages_map = [(package, device.get_package_instance(package)) for package in packages]
    return direct_to_template(request, 'devices/device_data_object_list.html', {
        'device': device,
        'new_device': 'new' in request.GET and request.GET['new'].lower() in ['', 'true'],
        'packages_map': packages_map,
    })

def test(request):
    # Some device
    device = get_object_or_404(Device, pk=1)
    # ...11 = ifInUcastPkts, ...16 = ifOutOctets
    oid = '1.3.6.1.2.1.2.2.1.16'
    # vHost's 3rd interface (not the loopback - 1, or the other NIC - 2)
    suffix = '3'

    duration = 50*24+10 # mintues
    granularity = 5 # minutes

    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=duration)
    new_minute = cutoff.minute - cutoff.minute % granularity
    start_time = datetime.datetime(cutoff.year, cutoff.month, cutoff.day, cutoff.hour, new_minute)

    # Get the data instances
    data_instances = DataInstance.objects.filter(data_object__identifier=oid, rule__device=device, suffix=suffix)#, created__gte=cutoff)

    # Return the data instances in a presentor
    return direct_to_template(request, 'devices/test.html', {
        'data_instances': CounterPresenter(data_instances, granularity=datetime.timedelta(minutes=granularity), start_time=start_time),
    })