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
from tinygraph.apps.data.cacher import cacher
from django.db.models import Q

import datetime

NUM_INTERFACES = 'iso.org.dod.internet.mgmt.mib-2.interfaces.ifNumber'
INTERFACE_INDEX = 'iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifIndex'
INTERFACE_MTU = 'iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifMtu'
INTERFACE_TYPE = 'iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifType'
INTERFACE_DESCR = 'iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr'
INTERFACE_PHYS_ADDRESS = 'iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifPhysAddress'

HOST_SYSTEM_PROCESSES = 'iso.org.dod.internet.mgmt.mib-2.host.hrSystem.hrSystemProcesses'
HOST_SYSTEM_UPTIME = 'iso.org.dod.internet.mgmt.mib-2.host.hrSystem.hrSystemUptime'
HOST_SYSTEM_NUM_USERS = 'iso.org.dod.internet.mgmt.mib-2.host.hrSystem.hrSystemNumUsers'
HOST_SYSTEM_MAX_PROCESSES = 'iso.org.dod.internet.mgmt.mib-2.host.hrSystem.hrSystemMaxProcesses'

SYSTEM_DESCR = 'iso.org.dod.internet.mgmt.mib-2.system.sysDescr'
SYSTEM_UPTIME = 'iso.org.dod.internet.mgmt.mib-2.system.sysUpTime'
SYSTEM_CONTACT = 'iso.org.dod.internet.mgmt.mib-2.system.sysContact'
SYSTEM_NAME = 'iso.org.dod.internet.mgmt.mib-2.system.sysName'
SYSTEM_CONTACT = 'iso.org.dod.internet.mgmt.mib-2.system.sysLocation'

def device_list(request):
    return direct_to_template(request, 'devices/device_list.html', {
        'devices': Device.objects.all(),
    })

def _get_interface_details(device_slug, index):
    if_index = str(cacher[(device_slug, INTERFACE_INDEX, str(index))][0])
    phys_address = cacher[(device_slug, INTERFACE_PHYS_ADDRESS, if_index)][0]
    if phys_address:
        phys_address = ':'.join('%0.2x' % int(n) for n in phys_address.split(' '))
    
    return {
        'index': if_index,
        'mtu': cacher[(device_slug, INTERFACE_MTU, if_index)][0],
        'type': cacher[(device_slug, INTERFACE_TYPE, if_index)][0],
        'description': cacher[(device_slug, INTERFACE_DESCR, if_index)][0],
        'physical_address': phys_address,
    }

def device_detail(request, device_slug):
    device = get_object_or_404(Device, slug=device_slug)
    enabled_package_instances = PackageInstance.objects.filter(device=device, 
        enabled=True).select_related()
    package_instances = [
        (
            package_instance, None, None
            # package_instance.memberships.filter(
            #     Q(graphed=True) & ~ \
            #     Q(package_membership__data_object__value_type__in=['counter'])
            # ).select_related(),
            # package_instance.memberships.filter(
            #     graphed=True,
            #     package_membership__data_object__value_type__in=['counter'],
            # ).select_related(),
            
        ) for package_instance in enabled_package_instances]
    
    slug = device.slug
    
    
    num_interfaces = cacher[(slug, NUM_INTERFACES, '0')][0]
    interfaces = None
    if num_interfaces:
        num_interfaces = int(num_interfaces)
        interfaces = [_get_interface_details(slug, index) for index in range(1, num_interfaces + 1)]
    
        for interface in interfaces:
            if interface['physical_address'] == '':
                num_interfaces -= 1
    
    system_uptime, created = cacher[(slug, HOST_SYSTEM_UPTIME, '0')]
    if system_uptime:
        system_uptime = int(system_uptime) / 100
        diff = datetime.datetime.now() - created
        diff = datetime.timedelta(seconds=diff.seconds)
        system_uptime = datetime.timedelta(seconds=system_uptime) + diff
    
    details = {
        'number_of_interfaces': num_interfaces,
        'interfaces': interfaces,
        'system': {
            'description': cacher[(slug, SYSTEM_DESCR, '0')][0],
            'contact': cacher[(slug, SYSTEM_CONTACT, '0')][0],
            'name': cacher[(slug, SYSTEM_NAME, '0')][0],
            'location': cacher[(slug, SYSTEM_CONTACT, '0')][0],
        },
        'host': {
            'processes': cacher[(slug, HOST_SYSTEM_PROCESSES, '0')][0],
            'uptime': system_uptime,
            'num_users': cacher[(slug, HOST_SYSTEM_NUM_USERS, '0')][0],
            'max_processes': cacher[(slug, HOST_SYSTEM_MAX_PROCESSES, '0')][0],
        }
    }
            
    return direct_to_template(request, 'devices/device_detail.html', {
        'device': device,
        'events': device.event_set.all()[:20],
        'package_instances': package_instances,
        'details': details
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
    packages = Package.objects.all().select_related()
    packages_map = [(package, device.get_package_instance(package)) for package in packages]
    
    new_map = []
    for package, package_instance in packages_map:
        package_instance_map = {
            'package_instance': package_instance,
            'package_instance_memberships': package_instance.memberships.select_related(),
        }
        new_map.append((package, package_instance_map))
    
    return direct_to_template(request, 'devices/device_data_object_list.html', {
        'device': device,
        'new_device': 'new' in request.GET and request.GET['new'].lower() in ['', 'true'],
        'packages_map': new_map,
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