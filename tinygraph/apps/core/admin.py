from django.contrib import admin
from core.models import Rule, DataInstance, DataObject, MibUpload, Package, PackageInstance

admin.site.register(Rule)
admin.site.register(DataInstance)
admin.site.register(DataObject)
admin.site.register(MibUpload)
admin.site.register(Package)
admin.site.register(PackageInstance)