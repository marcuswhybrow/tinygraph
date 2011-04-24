from utils import PollDaemon, logging
from definitions.models import DataObject
from data.models import DataInstance
from devices.models import Device
from pysnmp.entity.rfc3413.oneliner import cmdgen
from tinygraph.apps.definitions.utils import snmp_value_to_str, \
     get_mib_view_controller, get_transport, get_authentication, \
     snmp_name_to_str
from django.conf import settings
from tinygraph.tinygraphd.signals import pre_poll, post_poll, poll_error, \
    value_change
from tinygraph.apps.rules.models import PackageInstanceMembership
import django.dispatch
from tinygraph.apps.data.settings import NON_INCREMENTAL_DATA_VALUE_TYPES
import socket

SNMP_GETBULK_SIZE = getattr(settings, 'TINYGRAPH_SNMP_GETBULK_SIZE', 25)
DEVICE_TRANSPORT_ERROR_MESSAGE = getattr(settings, 
    'TINYGRAPH_DEVICE_TRANSPORT_ERROR_MESSAGE', 
    'Could not connect to device.')

class TinyGraphDaemon(PollDaemon):
    
    def _callback(self, handle, error_indication, error_status, error_index, 
                  var_bind_table, context):
        """
        A callback which returns False to stop further bulk requests and True
        to continue
        """
        
        rule = context['rule']
        mvc = context['mvc']
        
        if error_indication is not None:
            logging.warning('SNMP GETBULK error "%s" for OID "%s" on '
                'device "%s". Error status: %s, error index: %s' %
                (error_indication, rule.data_object.get_identifier_tuple(),
                rule.device.user_given_name, error_status, error_index))
            return False
        
        if not var_bind_table:
            return False

        for row in var_bind_table:
            name, value = row[0]
            
            rule_oid = rule.data_object.get_identifier_tuple()
            try:
                if rule_oid != name[:len(rule_oid)]:
                    # This is not a child of the rule, do no more bulk 
                    # requests
                    return False
            except IndexError:
                # This is not a child of the rule, do no more bulk requests
                return False

            oid, label, suffix = mvc.getNodeName(name)

            identifier = snmp_name_to_str(name)
            if identifier is None:
                logging.warning('pysnmp returned "%s" as a name. Its value '
                    'was therefore not logged.' % name)
                continue

            str_oid = '.'.join([str(i) for i in oid])
            str_suffix = '.'.join([str(i) for i in suffix])

            try:
                data_object = DataObject.objects.get(identifier=str_oid)
            except DataObject.DoesNotExist:
                logging.error('The database representation of DataObjects '
                'does not match the MIB strucute. a DataObject with the '
                'OID "%s" could not be found.' % str_oid)
                continue

            value_type = None
            str_value = None

            value_type, str_value = snmp_value_to_str(value)

            if value_type == 'end_of_mib_view':
                return False
            elif value_type is None:
                logging.error('Unrecognised value "%s"' % value.__class__)
                continue
            
            prev_data_instance = None
            if (value_type in NON_INCREMENTAL_DATA_VALUE_TYPES):
                try:
                    prev_data_instance = DataInstance.objects.filter(
                        rule=rule, data_object=data_object, suffix=str_suffix
                    ).latest()
                except:
                    pass

            # Create the DataInstance
            new_data_instance = DataInstance.objects.create(rule=rule,
                data_object=data_object, suffix=str_suffix,
                value=str_value, value_type=value_type)
            
            if (value_type in NON_INCREMENTAL_DATA_VALUE_TYPES):
                if prev_data_instance is not None and (new_data_instance.value
                    != prev_data_instance.value):
                    value_change.send(sender=self, 
                        data_instance=new_data_instance)
        
        # The children of the rule have no yet been exhausted, continue with
        # the bulk requests
        return True
    
    def poll(self):
        """Called once for each poll (say every 5 minutes)"""
        
        mvc = get_mib_view_controller()
        asyn_command_generator = cmdgen.AsynCommandGenerator()
                
        for device in Device.objects.all():
            transport = get_transport(device)
            authentication = get_authentication(device)
            
            # If the transport could not be setup (usually a network error) or
            # the authentication details for the device were provided
            # incorrectly, then skip this device in the polling process
            if transport is None or authentication is None:
                poll_error.send(sender=self, device=device, 
                    message=DEVICE_TRANSPORT_ERROR_MESSAGE)
                continue
            
            pre_poll.send(sender=self, device=device)
            
            # Setup the asynchronous SNMP BULK requests (non blocking)
            package_instance_memberships = \
                PackageInstanceMembership.objects.filter(
                    package_instance__device=device, 
                    package_instance__enabled=True, enabled=True)
            for package_instance_membership in package_instance_memberships:
                rule = package_instance_membership.rule
                asyn_command_generator.asyncBulkCmd(
                    authentication,
                    transport,
                    0, SNMP_GETBULK_SIZE,
                    (rule.data_object.get_identifier_tuple(),),
                    (self._callback, {
                        'rule': rule,
                        'mvc': mvc,
                    })
                )
            
        # Blocks until all requests have returned
        asyn_command_generator.snmpEngine.transportDispatcher.runDispatcher()
        
        post_poll.send(sender=self, device=device)
                