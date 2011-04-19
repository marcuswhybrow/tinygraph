from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from tinygraph.apps.devices.models import Device
from tinygraph.apps.definitions.models import Package
from tinygraph.apps.rules.models import PackageInstance
from tinygraph.apps.data.models import DataInstance
from django.db.models import Count
import datetime
import itertools

def keyfunc(data_instance):
    return '%s.%s' % (data_instance.data_object, data_instance.suffix)

SINGULAR_VALUE_TYPES = ['octet_string', 'object_identifier', 'gauge', 'integer', 'time_ticks']

def package_instance_detail(request, device_slug, package_slug):
    device = get_object_or_404(Device, slug=device_slug)
    package = get_object_or_404(Package, slug=package_slug)
    package_instance = get_object_or_404(PackageInstance, device=device, package=package)
    rules = package_instance.rules.select_related()
    
    limit = datetime.datetime.now() - datetime.timedelta(days=1)
    
    rule_pairs = []
    for rule in rules:
        data_instances = rule.instances.filter(created__gte=limit).select_related()
        
        data_objects = []
        data = sorted(data_instances, key=keyfunc)
        for key, group in itertools.groupby(data, key=keyfunc):
            group = list(group)
            
            data = None
            data_instance = group[-1]
            data_object = data_instance.data_object
            suffix = data_instance.suffix
            value_type = data_instance.value_type
            
            if value_type in SINGULAR_VALUE_TYPES:
                data = data_instance.value
            else:
                data = group
            
            data_objects.append(({
                'data_object': data_object,
                'suffix': suffix,
                'value_type': value_type,
            }, data))
        
        rule_pairs.append((rule, data_objects))
        
    
    return direct_to_template(request, 'rules/package_instance_detail.html', {
        'device': device,
        'package': package,
        'package_instance': package_instance,
        'rules': rule_pairs,
        'singular_value_types': SINGULAR_VALUE_TYPES,
    })