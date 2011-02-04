from utils import PollDaemon, logging
from core.models import DataInstance, Device, DataObject
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
from pyasn1.type import univ
from pysnmp.smi.builder import MibBuilder
from pysnmp.smi.view import MibViewController
from pysnmp.smi.error import SmiError

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
    
    def poll(self):
        
        def poll_rule(rule):
            error_indication, error_status, error_index, var_bind_table = cmdgen.CommandGenerator().bulkCmd(
                cmdgen.CommunityData('TinyGraph', 'Whybrow', int(rule.device.snmp_version)-1),
                cmdgen.UdpTransportTarget((rule.device.user_given_address, rule.device.snmp_port or 161)),
                0,2000,
                rule.data_object.get_identifier_tuple()
            )
            
            mvc = self._get_mib_view_controller()
            
            if error_indication is not None:
                logging.warning('SNMP GETBULK error "%s" for OID "%s" on '
                    'device "%s". Error status: %s, error index: %s' %
                    (error_indication, rule.data_object.get_identifier_tuple(),
                    rule.device.user_given_name, error_status, error_index))
            
            for row in var_bind_table:
                name, value = row[0]
                
                oid, label, suffix = mvc.getNodeName(name)
                
                # I have never seen a name which was not a ObjectName instance
                if isinstance(name, rfc1902.ObjectName):
                    identifier = '.'.join([str(i) for i in name])
                else:
                    logging.warning('pysnmp returned "%s" as a name. Its value was therefore not logged.' % name)
                    continue
                
                oid, label, suffix = mvc.getNodeName(name)
                
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
                
                if isinstance(value, rfc1902.Integer):
                    value_type = 'integer'
                    str_value = str(value)
                elif isinstance(value, rfc1902.Integer32):
                    value_type = 'integer'
                    str_value = str(value)
                elif isinstance(value, rfc1902.OctetString):
                    value_type = 'octet_string'
                    str_value = '.'.join([str(ord(octet)) for octet in value])
                elif isinstance(value, rfc1902.IpAddress):
                    value_type = 'ip_address'
                    str_value = '.'.join([str(ord(octet)) for octet in value])
                elif isinstance(value, rfc1902.Counter32):
                    value_type = 'counter'
                    str_value = str(value)
                elif isinstance(value, rfc1902.Gauge32):
                    value_type = 'gauge'
                    str_value = str(value)
                elif isinstance(value, rfc1902.Unsigned32):
                    value_type = 'integer'
                    str_value = str(value)
                elif isinstance(value, rfc1902.TimeTicks):
                    value_type = 'time_ticks'
                    str_value = str(value)
                elif isinstance(value, rfc1902.Opaque):
                    value_type = 'opaque'
                    str_value = '.'.join([str(ord(octet)) for octet in value])
                elif isinstance(value, rfc1902.Counter64):
                    value_type = 'counter'
                    str_value = str(value)
                elif isinstance(value, rfc1902.Bits):
                    value_type = 'bit_string'
                    str_value = '.'.join([str(ord(octet)) for octet in value])
                
                elif isinstance(value, univ.ObjectIdentifier):
                    value_type = 'object_identifier'
                    str_value = '.'.join([str(i) for i in value])
                    
                else:
                    logging.error('Unrecognised value "%s"' % value.__class__)
                    continue
                
                # Create the DataInstance
                DataInstance.objects.create(rule=rule,
                    data_object=data_object, suffix=str_suffix,
                    value=str_value, value_type=value_type)
                    
        for device in Device.objects.all():
            for rule in device.rules.filter(enabled=True):
                poll_rule(rule)
                