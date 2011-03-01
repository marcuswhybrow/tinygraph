from piston.handler import BaseHandler
from tinygraph.apps.rules.models import Rule, PackageInstance

class RuleHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Rule

class PackageInstanceHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = PackageInstance