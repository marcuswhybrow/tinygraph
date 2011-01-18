from django.contrib import admin
from tinygraph.apps.core.models import Device, Rule, Data, DataObject, Protocol

admin.site.register(Device)
admin.site.register(Rule)
admin.site.register(Data)
admin.site.register(DataObject)
admin.site.register(Protocol)