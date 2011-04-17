from django.contrib import admin
from tinygraph.apps.events.models import Event

class EventAdmin(admin.ModelAdmin):
    # data_instance must be excluded. Django attempts to create a drop down
    # box containing all the data instances ever logged (which would be
    # thousands.)
    exclude = ('data_instance',)

admin.site.register(Event, EventAdmin)