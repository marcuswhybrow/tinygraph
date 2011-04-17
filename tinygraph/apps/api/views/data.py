from tinygraph.apps.api.utils import ImprovedHandler
from tinygraph.apps.data.models import DataInstance

class DataInstanceHandler(ImprovedHandler):
    allowed_methods = ('GET',)
    model = DataInstance