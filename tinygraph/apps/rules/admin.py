from django.contrib import admin
from rules.models import Rule, DataInstance, PackageInstance

admin.site.register(Rule)
admin.site.register(DataInstance)
admin.site.register(PackageInstance)