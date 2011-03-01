from piston.handler import BaseHandler
from tinygraph.apps.definitions.models import DataObject, Package, MibUpload

class DataObjectHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = DataObject
    fields = ('identifier', 'user_given_name', 'derived_name')
    exclude = ('parent',)

class PackageHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = Package
    fields = ('description', 'created', 'editable', 'slug', 'title')

class MibUploadHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = MibUpload