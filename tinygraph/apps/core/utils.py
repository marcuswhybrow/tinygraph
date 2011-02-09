from pysnmp.smi.builder import MibBuilder
from pysnmp.smi.view import MibViewController
from pysnmp.smi.error import SmiError
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902, rfc1905
from pyasn1.type import univ
from django.conf import settings

import logging
import time

LOG_FILENAME = getattr(settings, 'TINYGRAPH_TINYGRAPH_LOG_FILENAME', '/tmp/tinygraph.log')
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SNMP_DEFAULT_PORT = getattr(settings, 'TINYGRAPH_SNMP_DEFAULT_PORT', 161)
SNMP_AGENT_NAME = getattr(settings, 'TINYGRAPH_SNMP_AGENT_NAME', 'TinyGraph')

def get_mib_view_controller():
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

def snmp_name_to_str(name):
    # I have never seen a name which was not a ObjectName instance
    if isinstance(name, rfc1902.ObjectName):
        return '.'.join(str(i) for i in name)
    return None

def snmp_value_to_str(value):
    
    def is_ascii(s):
        return all(ord(c) < 128 for c in s)
    
    def octet(v):
        if is_ascii(v):
            return str(v)
        else:
            return ' '.join(str(ord(octet)) for octet in value)
    
    if isinstance(value, rfc1902.Integer):
        return 'integer', str(value)
    elif isinstance(value, rfc1902.Integer32):
        return 'integer', str(value)
    elif isinstance(value, rfc1902.OctetString):
        return 'octet_string', octet(value)
    elif isinstance(value, rfc1902.IpAddress):
        return 'ip_address', '.'.join(str(ord(octet)) for octet in value)
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
        return 'object_identifier', '.'.join(str(i) for i in value)
        
    elif isinstance(value, rfc1905.EndOfMibView):
        return 'end_of_mib_view', None
    
    return None, None

def get_transport(device):
    try:
        return cmdgen.UdpTransportTarget((device.user_given_address, device.snmp_port or SNMP_DEFAULT_PORT))
    except socket.gaierror, e:
        logging.error('Problem setting up the UDP transport for "%s": %s' % (device, e))
    return None


def get_authentication(device):
    v = device.snmp_version
    try:
        if v == '1':
            return cmdgen.CommunityData(SNMP_AGENT_NAME, 'Whybrow', 0)
        elif v == '2':
            return cmdgen.CommunityData(SNMP_AGENT_NAME, 'Whybrow', 1)
        elif v == '3':
            return cmdgen.UsmUserData('my-user', 'my-authkey', 'my-privkey'),
        else:
            logging.error('Unknown SNMP version "%s" for device "%s"' % (v, device))
    except Exception, e:
        logging.error('Problem setting up version "%s" SNMP authentication for device "%s": %s' % (v, device, e))
    return None


def datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())