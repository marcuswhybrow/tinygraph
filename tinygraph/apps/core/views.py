from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template
from tinygraph.apps.core.models import Device, Protocol, ProtocolVersion, DataObject

def device_list(request):
    return direct_to_template(request, 'core/device_list.html', {
        'devices': Device.objects.all(),
    })

def protocol_list(request):
    return direct_to_template(request, 'core/protocol_list.html', {
        'protocols': Protocol.objects.all(),
    })
    
def protocol_detail(request, protocol_slug):
    return direct_to_template(request, 'core/protocol_detail.html', {
        'protocol': get_object_or_404(Protocol, slug=protocol_slug)
    })
    
def protocol_version_detail(request, protocol_slug, protocol_version_slug):
    return direct_to_template(request, 'core/protocol_version_detail.html', {
        'protocol_version': get_object_or_404(ProtocolVersion, protocol__slug=protocol_slug, slug=protocol_version_slug),
    })