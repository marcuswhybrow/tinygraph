from piston.handler import BaseHandler
from tinygraph.apps.data.models import DataInstance

class DataInstanceHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = DataInstance