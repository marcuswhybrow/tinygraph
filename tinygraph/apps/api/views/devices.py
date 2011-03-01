from piston.handler import BaseHandler
from tinygraph.apps.devices.models import Device

class DeviceHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Device
    # fields = ('snmp_version', 'snmp_port', 'fqdn', 'user_given_address', 'user_given_name', 'ip_address', 'slug')