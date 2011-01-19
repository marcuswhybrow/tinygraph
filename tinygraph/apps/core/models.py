from django.db import models
from django.template.defaultfilters import slugify

class Device(models.Model):
    """A device on the network"""
    
    user_given_name = models.CharField(blank=True, max_length=100,
                                       help_text='A friendly name for this \
                                       device which you will understand.')
    
    # 255 characters is the maximum length of a host name for DNS
    host_name = models.CharField(blank=True, max_length=255,
                                 help_text='A DNS name that will resolve to \
                                 an IP address for this device.')
    # 45 characters is the maximum length of an IPv6 address
    address = models.CharField(max_length=45, help_text='An IP address for \
                                                         this device.')
    
    def __unicode__(self):
        if self.user_given_name:
            return self.user_given_name
        elif self.host_name:
            return '%s (%s)' % (self.host_name, self.address)
        else:
            return self.address
        

class Protocol(models.Model):
    """Protocols used to gather data about devices"""
    
    name = models.CharField(blank=True, max_length=255,
                            help_text='The full name of this Protocol, for \
                            example "Simple Network Management Protocol".')
    acronym = models.CharField(max_length=20, help_text='The shorter common \
                               name for this Protocol, for example "SNMP".')
    slug = models.SlugField(unique=True, editable=False)
    description = models.TextField(blank=True,
                                   help_text='A helpful description of this \
                                   protocol for uninitiated users. It should \
                                   give a sense of the role this protocol \
                                   plays in the operation of the system and \
                                   cover any specifc traits.')
        
    def __unicode__(self):
        return self.acronym
    
    @models.permalink
    def get_absolute_url(self):
        return ('tinygraph.apps.core.views.protocol_detail', (), {
            'protocol_slug': self.slug,
        })
    
    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.acronym))
        super(Protocol, self).save(*args, **kwargs)

class ProtocolVersion(models.Model):
    """An instance of a Protocol at a particular version"""
    
    class Meta:
        unique_together = ('slug', 'protocol')
    
    protocol = models.ForeignKey(Protocol, related_name='versions')
    version = models.CharField(max_length=20, help_text='The version number \
                               of the Protocol for example "1", "2c", "3" in \
                               the case of SNMP.')
    slug = models.SlugField(editable=False)
    description = models.TextField(blank=True,
                                   help_text='Reasons why this version of \
                                   the protocol exists, and an outline of \
                                   what is necessary to use it.')
    
    def __unicode__(self):
        return '%sv%s' % (self.protocol, self.version)
        
    @models.permalink
    def get_absolute_url(self):
        return ('tinygraph.apps.core.views.protocol_version_detail', (), {
            'protocol_slug': self.protocol.slug,
            'protocol_version_slug': self.slug,
        })
    
    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.version))
        super(ProtocolVersion, self).save(*args, **kwargs)

class DataObject(models.Model):
    """A piece of data retrievable via a protocol from a host"""
    
    identifier = models.CharField(max_length=255)
    protocol = models.ForeignKey(Protocol)
    derived_name = models.CharField(blank=True, max_length=255)
    user_given_name = models.CharField(blank=True, max_length=255)
    
    def __unicode__(self):
        return '%s - %s' % (self.user_given_name or self.derived_name or
                            self.identifier, self.protocol)
        
class Rule(models.Model):
    """Defines that a DataObject should be recorded for a particular Device"""
    
    data_object = models.ForeignKey(DataObject)
    device = models.ForeignKey(Device)
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return '%s - %s' % (self.data_object, self.device)

class DataInstance(models.Model):
    """Data collected for a Rule regarding a DataObject"""
    
    rule = models.ForeignKey(Rule)
    value = models.CharField(blank=True, max_length=1024)
    
    def __unicode__(self):
        return '%s - %s' % (self.value, self.rule)

