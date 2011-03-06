from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.dashboard import BoardHandler, ItemHandler, ConnectionHandler

board_handler = Resource(BoardHandler)
item_handler = Resource(ItemHandler)
connection_handler = Resource(ConnectionHandler)

urlpatterns = patterns('',
    url(r'^board/$', board_handler, name='board'),
    url(r'^board/(?P<id>\d+)/$', board_handler, name='board'),
    
    url(r'^item/$', item_handler, name='item'),
    url(r'^item/(?P<id>\d+)/$', item_handler, name='item'),
    
    url(r'^connection/$', connection_handler, name='connection'),
    url(r'^connection/(?P<id>\d+)/$', connection_handler, name='connection'),
)