from utils import PollDaemon, logging
from core.models import DataInstance, Device, DataObject
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902, rfc1905
from pyasn1.type import univ
from pysnmp.smi.builder import MibBuilder
from pysnmp.smi.view import MibViewController
from pysnmp.smi.error import SmiError
from django.conf import settings
import socket

SNMP_GETBULK_SIZE = getattr(settings, 'TINYGRAPH_SNMP_GETBULK_SIZE', 25)

class TinyGraphDaemon(PollDaemon):
    
    def _get_mib_view_controller(self):
        try:
            # Try and load MIB modules even from the users uploads
            mvc = MibViewController(MibBuilder().loadModules())
        except SmiError:
            # If somehow the user managed to bypass the validation and
            # upload the same MIB twice an SmiError will be thrown.
            logging.warning('The user has uploaded duplicate MIB files, ignoring all user upload MIB files!')
            
            # In which case we should try again without loading the user
            # uploaded MIB files
            mb = MibBuilder()
            mib_paths = mb.getMibPath()
            try:
                # Identify the position of the user upload path
                i = mib_paths.index(os.environ['PYSNMP_MIB_DIR'])
            except (KeyError, ValueError):
                return None
            else:
                # Remove the user upload path from the paths we are going
                # to use.
                mib_paths = mib_paths[:i] + mib_paths[i+1:]
                mb.setMibPath(*mib_paths)
                
                # Try again
                try:
                    mvc = MibViewController(mb.loadModules())
                except SmiError:
                    # Nothing we can do now, its a problem with "pysnmp"
                    logging.error('There is a problem with MIB store in "pysnmp".')
                    return None
        return mvc
    
    def _convert(self, value):
        
        def octet(v):
            try:
                return str(v)
            except:
                return ' '.join([str(ord(octet)) for octet in value])
        
        if isinstance(value, rfc1902.Integer):
            return 'integer', str(value)
        elif isinstance(value, rfc1902.Integer32):
            return 'integer', str(value)
        elif isinstance(value, rfc1902.OctetString):
            return 'octet_string', octet(value)
        elif isinstance(value, rfc1902.IpAddress):
            return 'ip_address', octet(value)
        elif isinstance(value, rfc1902.Counter32):
            return 'counter', str(value)
        elif isinstance(value, rfc1902.Gauge32):
            return 'gauge', str(value)
        elif isinstance(value, rfc1902.Unsigned32):
            return 'integer', str(value)
        elif isinstance(value, rfc1902.TimeTicks):
            return 'time_ticks', str(value)
        elif isinstance(value, rfc1902.Opaque):
            return 'opaque', octet(value)
        elif isinstance(value, rfc1902.Counter64):
            return 'counter', str(value)
        elif isinstance(value, rfc1902.Bits):
            return 'bit_string', octet(value)

        elif isinstance(value, univ.ObjectIdentifier):
            return 'object_identifier', '.'.join([str(i) for i in value])
            
        elif isinstance(value, rfc1905.EndOfMibView):
            return 'end_of_mib_view', None
        
        return None, None
    
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

            # I have never seen a name which was not a ObjectName instance
            if isinstance(name, rfc1902.ObjectName):
                identifier = '.'.join([str(i) for i in name])
            else:
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

            value_type, str_value = self._convert(value)

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
        logging.info('%2d returning True' % handle)
        return True
    
    def poll(self):
        """Called once for each poll (say every 5 minutes)"""
        
        mvc = self._get_mib_view_controller()
        asyn_command_generator = cmdgen.AsynCommandGenerator()
                
        for device in Device.objects.all():
            try:
                transport = cmdgen.UdpTransportTarget((device.user_given_address, device.snmp_port or 161))
            except socket.gaierror, e:
                logging.error('Problem setting up the UDP transport for "%s": %s' % (device, e))
                continue
            
            try:
                authentication = cmdgen.CommunityData('TinyGraph', 'Whybrow', int(device.snmp_version)-1)
            except Exception, e:
                logging.error('Problem setting up the SNMP authentication for "%s": %s' % (device, e))
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
                