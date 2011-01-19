from django.contrib import admin
from core.models import Device, Rule, DataInstance, DataObject

admin.site.register(Device)
admin.site.register(Rule)
admin.site.register(DataInstance)
admin.site.register(DataObject)