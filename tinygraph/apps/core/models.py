from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError

class DataObject(models.Model):
    """A piece of data retrievable via a protocol from a host"""
    
    identifier = models.CharField(max_length=255, db_index=True)
    derived_name = models.CharField(blank=True, max_length=255)
    user_given_name = models.CharField(blank=True, max_length=255)
    
    def __unicode__(self):
        return self.user_given_name or self.derived_name or self.identifier

class Device(models.Model):
    """A device on the network"""

    user_given_name = models.CharField(unique=True, max_length=100, help_text='A friendly name for this device which you will understand.')

    # 255 characters is the maximum length of a host name for DNS
    host_name = models.CharField(blank=True, max_length=255, help_text='A DNS name that will resolve to an IP address for this device.')
    # 45 characters is the maximum length of an IPv6 address
    address = models.CharField(max_length=45, help_text='An IP address for this device.')

    slug = models.SlugField(unique=True, editable=False, db_index=True)

    data_objects = models.ManyToManyField(DataObject, through='Rule')

    def __unicode__(self):
        return self.user_given_name

    @models.permalink
    def get_absolute_url(self):
        return ('core.views.device_detail', (), {
            'device_slug': self.slug,
        })

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.user_given_name))
        super(Device, self).save(*args, **kwargs)

class Rule(models.Model):
    """Defines that a DataObject should be recorded for a particular Device"""
    
    data_object = models.ForeignKey(DataObject, db_index=True)
    device = models.ForeignKey(Device, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return '%s - %s' % (self.data_object, self.device)


class DataInstance(models.Model):
    """Data collected for a Rule regarding a DataObject"""
    
    rule = models.ForeignKey(Rule, db_index=True)
    value = models.CharField(blank=True, max_length=1024)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    
    def __unicode__(self):
        return '%s - %s' % (self.value, self.rule)