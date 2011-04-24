from piston.handler import BaseHandler
from tinygraph.apps.definitions.models import DataObject, Package, \
    MibUpload, PackageMembership


class DataObjectHandler(BaseHandler):
    model = DataObject
    fields = ('identifier', 'user_given_name', 'derived_name')
    exclude = ('parent',)

class PackageHandler(BaseHandler):
    model = Package
    fields = ('description', 'created', 'editable', 'slug', 'title')

class MibUploadHandler(BaseHandler):
    model = MibUpload

class PackageMembershipHandler(BaseHandler):
    model = PackageMembership