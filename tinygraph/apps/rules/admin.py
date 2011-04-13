from django.contrib import admin
from tinygraph.apps.rules.models import Rule, PackageInstance

admin.site.register(Rule)
admin.site.register(PackageInstance)