from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from tinygraph.apps.devices.models import Device
from tinygraph.apps.definitions.models import Package
from tinygraph.apps.rules.models import PackageInstance
from tinygraph.apps.data.models import DataInstance, Poll
from django.db.models import Count
from django.core.cache import cache
from tinygraph.apps.data.cacher import cacher
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
                print index_column_derived_name
                instances = DataInstance.objects.filter(
                    poll=last_poll,
                    data_object__derived_name=index_column_derived_name,
                ).values('value')
                if instances:
                    for instance in instances:
                        index = instance['value']
                        cells = []
                        for column in table['columns']:
                            if column['name'] == 'Index':
                                cells.append(index)
                            else:
                                value = cacher[(
                                    device.slug,
                                    column['full_name'],
                                    index,
                                )][0]
                                cells.append(value)
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