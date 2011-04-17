from tinygraph.apps.api.utils import ImprovedHandler
from tinygraph.apps.devices.models import Device

class DeviceHandler(ImprovedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Device