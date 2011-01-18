from django.db import models

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
    address = models.CharField(blank=True, max_length=45,
                               help_text='An IP address for this device.')
    
    def __unicode__(self):
        if self.user_given_name:
            return self.user_given_name
        elif self.host_name and self.address:
            return '%s (%s)' % (self.host_name, self.address)
        else:
            return self.host_name or self.address or 'Device'
        

class Protocol(models.Model):
    """Protocols used to gather data about devices"""
    
    name = models.CharField(blank=True, max_length=255,
                            help_text='The full name of this Protocol, for \
                            example "Simple Network Management Protocol".')
    acronym = models.CharField(max_length=20, help_text='The shorter common \
                               name for this Protocol, for example "SNMP".')
    version = models.CharField(blank=True, max_length=20,
                               help_text='The version number of the Protocol \
                               for example "1", "2c", "3" in the case of SNMP\
                               .')
        
    def __unicode__(self):
        if self.acronym and self.version:
            return '%sv%s' % (self.acronym, self.version)
        else:
            return self.acronym

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

