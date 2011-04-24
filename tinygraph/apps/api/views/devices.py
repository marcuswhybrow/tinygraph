from piston.handler import BaseHandler
from tinygraph.apps.devices.models import Device

class DeviceHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Device