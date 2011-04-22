from django.contrib import admin
from tinygraph.apps.rules.models import Rule, PackageInstance, PackageRule, \
    PackageInstanceMembership

admin.site.register(Rule)
admin.site.register(PackageRule)
admin.site.register(PackageInstance)
admin.site.register(PackageInstanceMembership)