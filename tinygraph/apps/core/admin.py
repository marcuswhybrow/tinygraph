from django.contrib import admin
from tinygraph.apps.core.models import Device, Rule, DataInstance, DataObject, Protocol

admin.site.register(Device)
admin.site.register(Rule)
admin.site.register(DataInstance)
admin.site.register(DataObject)
admin.site.register(Protocol)