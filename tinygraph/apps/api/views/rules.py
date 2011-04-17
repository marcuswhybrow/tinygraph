from tinygraph.apps.api.utils import CsrfBaseHandler
from tinygraph.apps.rules.models import Rule, PackageInstance
from tinygraph.apps.devices.models import Device
from tinygraph.apps.definitions.models import Package

class RuleHandler(CsrfBaseHandler):
    model = Rule

class PackageInstanceHandler(CsrfBaseHandler):
    model = PackageInstance
    
    def _resolve_fks(self, request):
        dct = request.data.copy()
        
        if 'package' in dct:
            try:
                dct['package'] = Package.objects.get(pk=dct['package'])
            except Board.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('Board with primary key "%d" not found.' % dct['package'])
                return resp
        
        if 'device' in dct:
            try:
                dct['device'] = Device.objects.get(pk=dct['device'])
            except Device.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('Device with primary key "%d" not found.' % dct['device'])
                return resp
        request.data = dct
        return None
    
    def create(self, request):
        return self._resolve_fks(request) or super(PackageInstanceHandler, self).create(request)
    
    def update(self, request, *args, **kwargs):
        return self._resolve_fks(request) or super(PackageInstanceHandler, self).update(request, *args, **kwargs)