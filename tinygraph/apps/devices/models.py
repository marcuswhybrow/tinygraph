from django.db import models
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from tinygraph.tinygraphd.signals import pre_poll, post_poll, poll_error, \
    value_change
from django.dispatch import receiver
from tinygraph.apps.events.models import Event, ChangeEvent
from tinygraph.apps.rules.models import PackageInstance
import socket

SNMP_VERSIONS = (
    ('1', '1'),
    ('2', '2c'),
    ('3', '3'),
)

@receiver(pre_poll)
def pre_poll_callback(sender, **kwargs):
    """
    Performs potentially blocking calls WHICH IS BAD. This kind of work should
    be put on a job queue, however it is easier just to delay the poll a little
    bit.
    """
    device = kwargs.get('device')
    
    Event.objects.create(device=device, message='Started polling.')
    
    if device is not None:
        device.fqdn = socket.getfqdn(device.user_given_address)
        # This call only supports IPv4 addresses
        device.ip_address = socket.gethostbyname(device.user_given_address)
        device.save()

@receiver(post_poll)
def post_poll_callback(sender, **kwargs):
    """Called after each poll is conducted"""
    device = kwargs.get('device')
    if device is not None:
        Event.objects.create(device=device, message='Finished Polling.')

@receiver(poll_error)
def poll_error_callback(sender, **kwargs):
    """Called if there was an error connecting to the device"""
    device = kwargs.get('device')
    message = kwargs.get('message')
    if device is not None and message is not None:
        Event.objects.create(device=device, message=message)

@receiver(value_change)
def value_change_callback(sender, **kwargs):
    """Called if a new data instance is different to the previous value."""
    data_instance = kwargs.get('data_instance')
    if data_instance is not None:
        ChangeEvent.objects.create(device=data_instance.rule.device, data_instance=data_instance)

class Device(models.Model):
    """A device on the network"""

    user_given_name = models.CharField(unique=True, max_length=100, help_text='A friendly name for this device which you will understand.')

    # 255 characters is the maximum length of a host name for DNS
    user_given_address = models.CharField(max_length=255, help_text='An IP address or DNS name which will resolve into an IP address for this device.')
    
    ip_address = models.CharField(blank=True, max_length=39)
    fqdn = models.CharField(blank=True, max_length=255)

    slug = models.SlugField(unique=True, editable=False, db_index=True)

    data_objects = models.ManyToManyField('definitions.DataObject', through='rules.Rule', related_name='devices')
    packages = models.ManyToManyField('definitions.Package', through='rules.PackageInstance', related_name='devices')
    
    snmp_version = models.CharField(max_length=1, choices=SNMP_VERSIONS, help_text='2c recommended.')
    snmp_port = models.PositiveIntegerField(blank=True, null=True, help_text='Leave blank for default (162).')

    def __unicode__(self):
        return self.user_given_name

    @models.permalink
    def get_absolute_url(self):
        return ('devices:device_detail', (), {
            'device_slug': self.slug,
        })

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.user_given_name))
        super(Device, self).save(*args, **kwargs)
    
    def get_package_instance(self, package):
        try:
            return PackageInstance.objects.get(device=self, package=package)
        except:
            return None