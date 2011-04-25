from django.contrib import admin
from tinygraph.apps.data.models import DataInstance, Poll

admin.site.register(DataInstance)
admin.site.register(Poll)