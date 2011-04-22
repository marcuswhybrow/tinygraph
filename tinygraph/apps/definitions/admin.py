from django.contrib import admin
from tinygraph.apps.definitions.models import DataObject, MibUpload, \
    Package, PackageMembership

admin.site.register(DataObject)
admin.site.register(MibUpload)
admin.site.register(Package)
admin.site.register(PackageMembership)