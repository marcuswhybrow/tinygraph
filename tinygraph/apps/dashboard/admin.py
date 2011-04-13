from django.contrib import admin
from tinygraph.apps.dashboard.models import Board, Item, Connection

admin.site.register(Board)
admin.site.register(Item)
admin.site.register(Connection)