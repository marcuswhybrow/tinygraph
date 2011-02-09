from utils import PollDaemon, logging
from data.models import DataObject
from core.models import DataInstance
from devices.models import Device
from pysnmp.entity.rfc3413.oneliner import cmdgen
from tinygraph.apps.core.utils import snmp_value_to_str, \
     get_mib_view_controller, get_transport, get_authentication, \
     snmp_name_to_str
from django.conf import settings
import socket

SNMP_GETBULK_SIZE = getattr(settings, 'TINYGRAPH_SNMP_GETBULK_SIZE', 25)

class TinyGraphDaemon(PollDaemon):
    
    def _callback(self, handle, error_indication, error_status, error_index, var_bind_table, context):
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
                    # This is not a child of the rule, do no more bulk requests
                    return False
            except IndexError:
                # This is not a child of the rule, do no more bulk requests
                return False

            oid, label, suffix = mvc.getNodeName(name)

            identifier = snmp_name_to_str(name)
            if identifier is None:
                logging.warning('pysnmp returned "%s" as a name. Its value was therefore not logged.' % name)
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

            # Create the DataInstance
            DataInstance.objects.create(rule=rule,
                data_object=data_object, suffix=str_suffix,
                value=str_value, value_type=value_type)
        
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
                # TODO Add an event which notifies the user that there auth
                #      details might be incorrect
                continue
            
            # Setup the asynchronous SNMP BULK requests (non blocking)
            for rule in device.rules.filter(enabled=True):
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
                