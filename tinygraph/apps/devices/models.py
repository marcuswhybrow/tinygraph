from django.db import models
from django.template.defaultfilters import slugify

SNMP_VERSIONS = (
    ('1', '1'),
    ('2', '2c'),
    ('3', '3'),
)

class Device(models.Model):
    """A device on the network"""

    user_given_name = models.CharField(unique=True, max_length=100, help_text='A friendly name for this device which you will understand.')

    # 255 characters is the maximum length of a host name for DNS
    user_given_address = models.CharField(max_length=255, help_text='An IP address or DNS name which will resolve into an IP address for this device.')
    
    ip_address = models.CharField(blank=True, max_length=39)
    fqdn = models.CharField(blank=True, max_length=255)

    slug = models.SlugField(unique=True, editable=False, db_index=True)

    data_objects = models.ManyToManyField('core.DataObject', through='core.Rule', related_name='devices')
    packages = models.ManyToManyField('core.Package', through='core.PackageInstance', related_name='devices')
    
    snmp_version = models.CharField(max_length=1, choices=SNMP_VERSIONS)
    snmp_port = models.PositiveIntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.user_given_name

    @models.permalink
    def get_absolute_url(self):
        return ('devices.views.device_detail', (), {
            'device_slug': self.slug,
        })

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.user_given_name))
        super(Device, self).save(*args, **kwargs)