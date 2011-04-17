from tinygraph.apps.api.utils import ImprovedHandler
from tinygraph.apps.definitions.models import DataObject, Package, MibUpload

class DataObjectHandler(ImprovedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = DataObject
    fields = ('identifier', 'user_given_name', 'derived_name')
    exclude = ('parent',)

class PackageHandler(ImprovedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Package
    fields = ('description', 'created', 'editable', 'slug', 'title')

class MibUploadHandler(ImprovedHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = MibUpload