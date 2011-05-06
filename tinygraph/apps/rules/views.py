from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from tinygraph.apps.devices.models import Device
from tinygraph.apps.definitions.models import Package, DataObject
from tinygraph.apps.rules.models import PackageInstance, PackageInstanceMembership
from tinygraph.apps.data.models import DataInstance, Poll
from django.db.models import Count
from django.core.cache import cache
from tinygraph.apps.data.cacher import cacher
from tinygraph.apps.definitions.cacher import cacher as definitions_cacher
from tinygraph.apps.data.presenters import CounterPresenter
import datetime
import itertools

def keyfunc(data_instance):
    return '%s.%s' % (data_instance['data_object'], data_instance['suffix'])

SINGULAR_VALUE_TYPES = ['octet_string', 'object_identifier', 'gauge', 'integer', 'time_ticks']

def package_instance_detail(request, device_slug, package_slug):
    device = get_object_or_404(Device, slug=device_slug)
    package = get_object_or_404(Package, slug=package_slug)
    package_instance = get_object_or_404(PackageInstance, device=device, package=package)
    
    package_instance_memberships = package_instance.memberships.select_related()
    
    tables = {}
    individuals = {}
    
    for package_instance_membership in package_instance_memberships:
        value_type = package_instance_membership.package_membership.data_object.value_type
        name = package_instance_membership.package_membership.data_object.derived_name
        identifier = package_instance_membership.package_membership.data_object.identifier
        
        name_list = name.split('.')
        identifier_list = identifier.split('.')
        
        # Determine if this data_object is part of a table
        is_part_of_table = False
        for part_count, part in enumerate(name_list):
            if part.endswith('Table'):
                is_part_of_table = True
                full_table_name = '.'.join(name_list[:part_count + 1])
                table_name = part[:-len('Table')]
                table = tables.get(full_table_name)
                if not table:
                    tables[full_table_name] = {
                        'name': table_name,
                        'full_name': full_table_name,
                        'identifier': '.'.join(identifier.split('.')[:part_count + 1]),
                        'entry_identifier': '.'.join(identifier.split('.')[:part_count + 2]),
                        'columns': [],
                        'rows': [],
                    }
            elif part.endswith('Entry'):
                is_part_of_table = True
                table_prefix = '.'.join(name_list[:part_count])
                table = tables.get(table_prefix)
                if table:
                    full_column_name = '.'.join(name_list[:part_count + 2])
                    long_column_name = name_list[part_count + 1]
                    column_name = long_column_name[len(table['name']):]
                    table['columns'].append({
                        'full_name': full_column_name,
                        'name': column_name,
                        'identifier': '.'.join(identifier.split('.')[:part_count + 2]),
                        'value_type': value_type,
                        'package_instance_membership_pk': package_instance_membership.pk,
                    })
                    break
                    
        if is_part_of_table == False:
            individuals[name] = {
                'full_name': name,
                'value': cacher[(device.slug, name, '0')][0],
            }
                
    
    try:
        last_poll = Poll.objects.latest()
    except Poll.DoesNotExist:
        # There is no data to display in the table as there has never been a 
        # poll
        pass
    else:
        for table in tables.values():
            index_column_derived_name = None
            for column in table['columns']:
                if column['identifier'][len(table['entry_identifier']):] == '.1':
                    index_column_derived_name = column['full_name']
                    break
            if index_column_derived_name:
                instances = DataInstance.objects.filter(
                    rule__device=device,
                    poll=last_poll,
                    data_object__derived_name=index_column_derived_name,
                ).values('value', 'data_object__pk')
                if instances:
                    for instance in instances:
                        index = instance['value']
                        cells = []
                        for column in table['columns']:
                            if column['name'] == 'Index':
                                value = index
                            else:
                                value = cacher[(
                                    device.slug,
                                    column['full_name'],
                                    index,
                                )][0]
                                if column['value_type'] == 'object_identifier':
                                    derived_name = definitions_cacher[value]
                                    if derived_name:
                                        value = derived_name.split('.')[-1]
                            cells.append({
                                'value': value,
                                'value_type': column['value_type'],
                                'suffix': index,
                                'derived_name': column['full_name'],
                                'identifier': column['identifier'],
                                'package_instance_membership_pk': column['package_instance_membership_pk'],
                            })
                        table['rows'].append(cells)
    
    data = {
        'tables': tables.values(),
        'individuals': individuals.values(),
    }
        
    
    return direct_to_template(request, 'rules/package_instance_detail.html', {
        'device': device,
        'package': package,
        'package_instance': package_instance,
        'package_instance_memberships': package_instance.memberships.select_related(),
        'data': data,
        # 'rules': rule_pairs,
        'singular_value_types': SINGULAR_VALUE_TYPES,
    })

def package_instance_membership_detail(request, device_slug, package_slug, data_object_derived_name, suffix):
    device = get_object_or_404(Device, slug=device_slug)
    package = get_object_or_404(Package, slug=package_slug)
    package_instance = get_object_or_404(PackageInstance, device=device, package=package)
    package_instance_membership = get_object_or_404(PackageInstanceMembership, package_instance=package_instance, package_membership__data_object__derived_name=data_object_derived_name)
    
    short_derived_name = package_instance_membership.package_membership.data_object.derived_name.split('.')[-1]
    
    instances = DataInstance.objects.filter(rule=package_instance_membership.rule, suffix=suffix)
    
    duration = 50*24+10 # mintues
    granularity = 5 # minutes

    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=duration)
    new_minute = cutoff.minute - cutoff.minute % granularity
    start_time = datetime.datetime(cutoff.year, cutoff.month, cutoff.day, cutoff.hour, new_minute)
    
    data = CounterPresenter(instances, granularity=datetime.timedelta(minutes=granularity), start_time=start_time)
    
    return direct_to_template(request, 'rules/package_instance_membership_detail.html', {
        'device': device,
        'package': package,
        'package_instance': package_instance,
        'package_instance_membership': package_instance_membership,
        'short_derived_name': short_derived_name,
        'suffix': suffix,
        'data': data,
    })