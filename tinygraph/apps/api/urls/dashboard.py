from django.conf.urls.defaults import *
from piston.resource import Resource
from api.views.dashboard import BoardHandler, ItemHandler, ConnectionHandler

# class ShitResource(Resource):
#     def __call__(self, request, *args, **kwargs):
#         print 'REQUEST', request.__dict__
#         return super(ShitResource, self).__call__(request, *args, **kwargs)

board_handler = Resource(BoardHandler)
item_handler = Resource(ItemHandler)
connection_handler = Resource(ConnectionHandler)

urlpatterns = patterns('',
    url(r'^board/$', board_handler, name='boards'),
    url(r'^board/(?P<id>\d+)/$', board_handler, name='board'),
    
    url(r'^item/$', item_handler, name='items'),
    url(r'^item/(?P<id>\d+)/$', item_handler, name='item'),
    
    url(r'^connection/$', connection_handler, name='connections'),
    url(r'^connection/(?P<id>\d+)/$', connection_handler, name='connection'),
)