from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.dashboard import BoardHandler, ItemHandler, ConnectionHandler

board_handler = Resource(BoardHandler)
item_handler = Resource(ItemHandler)
connection_handler = Resource(ConnectionHandler)

urlpatterns = patterns('',
    (r'^board/$', board_handler),
    (r'^board/(?P<id>\d+)/$', board_handler),
    
    (r'^item/$', item_handler),
    (r'^item/(?P<id>\d+)/$', item_handler),
    
    (r'^connection/$', connection_handler),
    (r'^connection/(?P<id>\d+)/$', connection_handler),
)