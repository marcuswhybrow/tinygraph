from tinygraph.apps.api.utils import ImprovedHandler
from tinygraph.apps.definitions.models import DataObject, Package, \
    MibUpload, PackageMembership


class DataObjectHandler(ImprovedHandler):
    model = DataObject
    fields = ('identifier', 'user_given_name', 'derived_name')
    exclude = ('parent',)

class PackageHandler(ImprovedHandler):
    model = Package
    fields = ('description', 'created', 'editable', 'slug', 'title')

class MibUploadHandler(ImprovedHandler):
    model = MibUpload

class PackageMembershipHandler(ImprovedHandler):
    model = PackageMembership