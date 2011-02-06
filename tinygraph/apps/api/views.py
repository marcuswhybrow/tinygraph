from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template
from django.http import Http404, HttpResponse
from core.models import DataObject, Device
from core.utils import snmp_value_to_str, get_mib_view_controller, logging, \
     get_transport, get_authentication, snmp_name_to_str
from pysnmp.entity.rfc3413.oneliner import cmdgen
import simplejson
import subprocess

GETBULK_MAX_SIZE = 100
ANALYSIS_STARTING_OID = (1,3,6,1) # iso.org.dod.internet

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
    if request.method == 'POST' and 'device_pk' in request.POST:
        device = get_object_or_404(Device, pk=request.POST['device_pk'])
        
        transport = get_transport(device)
        authentication = get_authentication(device)
        
        if transport is not None and authentication is not None:
            
            mvc = get_mib_view_controller()
            
            context = {
                'last_oid': None,
                'device': device,
                'oids': [],
                'mvc': mvc,
                'errors': {},
            }
            
            def callback(handle, error_indication, error_status, error_index, var_bind_table, context):
                for row in var_bind_table:
                    name, value = row[0]
                    oid, label, suffix = context['mvc'].getNodeName(name)
                    value_type, str_value = snmp_value_to_str(value)
                    
                    fields = {
                        'oid': snmp_name_to_str(name),
                        'lookup': {
                            'oid': snmp_name_to_str(oid),
                            'label': '.'.join(label),
                            'suffix': snmp_name_to_str(suffix),
                        },
                        'value': str_value,
                        'value_type': value_type,
                    }
                    
                    if value_type == 'object_identifier':
                        v_oid, v_label, v_suffix = context['mvc'].getNodeName(value)
                        fields['value_extra'] = {
                            'label': '.'.join(v_label),
                            'suffix': '.'.join(str(i) for i in v_suffix),
                        }
                        
                    context['oids'].append(fields)
                    context['last_oid'] = name
                
                if error_indication is not None:
                    context['errors'] = {
                        'error_indication': error_indication,
                        'error_status': error_status,
                        'error_index': error_index,
                    }
                    return False
                return True
                    
            
            asyn_command_generator = cmdgen.AsynCommandGenerator()
            command_generator = cmdgen.CommandGenerator()
            
            asyn_command_generator.asyncBulkCmd(
                authentication,
                transport,
                0, 10,
                (ANALYSIS_STARTING_OID,),
                (callback, context)
            )
            
            asyn_command_generator.snmpEngine.transportDispatcher.runDispatcher()
            
            data = {
                'oids': context['oids'],
                'errors': context['errors'],
                'last_oid': snmp_name_to_str(context['last_oid']),
            }
            
            error_indication, error_status, error_index, var_bind_table = command_generator.nextCmd(
                authentication,
                transport,
                (1,3,6,1,2,1,5)
            )
            
            print error_indication, error_status, error_index
            print var_bind_table
            
            # if error_indication is not None:
            #     data['errors'] = {
            #         'indication': error_indication,
            #         'status': error_status,
            #         'index': error_index,
            #     }
            
            # for row in var_bind_table:
            #     name, value = row[0]
            #     oid, label, suffix = mvc.getNodeName(name)
            #     data['oids'].append({
            #         'oid': name,
            #         'looked_up_oid': oid,
            #         'looked_up_label': label,
            #         'looked_up_suffix': suffix,
            #         'value': snmp_value_to_str(value),
            #     })
        
        return HttpResponse(simplejson.dumps(data), mimetype='application/json')
    raise Http404

def data_object_children_list(request):
    if request.is_ajax() and request.method == 'POST' and 'data_object_pk' in request.POST:
        data_object_pk = request.POST['data_object_pk']
        return direct_to_template(request, 'core/includes/data_object_children_list.html', {
            'data_object_children': DataObject.objects.filter(parent__pk=data_object_pk),
        })
    raise Http404