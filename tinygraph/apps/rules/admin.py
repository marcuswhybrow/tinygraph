from django.contrib import admin
from rules.models import Rule, PackageInstance

admin.site.register(Rule)
admin.site.register(PackageInstance)