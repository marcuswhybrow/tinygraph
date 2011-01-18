from django.db import models

class Device(models.Model):
    """A device on the network"""
    
    # 255 characters is the maximum length of a host name for DNS
    host_name = models.CharField(blank=True, max_length=255)
    
    # 45 characters is the maximum length of an IPv6 address
    address = models.CharField(blank=True, max_length=45)
    
    def __unicode__(self):
        return host_name or address or 'Device'
        

class Protocol(models.Model):
    """Protocols used to gather data about devices"""
    
    name = models.CharField(blank=True, max_length=255)
    acronym = models.CharField(blank=True, max_length=20)
    version = models.CharField(blank=True, max_length=20)
        
    def __unicode__(self):
        return '%s %s' % (acronym, version)
        

class DataObject(models.Model):
    """A piece of data retrievable via a protocol from a host"""
    
    identifier = models.CharField(max_length=255)
    protocol = models.ForeignKey(Protocol)
    derived_name = models.CharField(blank=True, max_length=255)
    user_given_name = models.CharField(blank=True, max_length=255)
    
    def __unicode__(self):
        return '%s - %s' % (user_given_name or derived_name or identifier,
                            protocol)
        
class Rule(models.Model):
    """Defines that a DataObject should be recorded for a particular Device"""
    
    data_object = models.ForeignKey(DataObject)
    device = models.ForeignKey(Device)
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return '%s - %s' % (data_object, device)

class Data(models.Model):
    """Data collected for a Rule"""
    
    class Meta:
        verbose_name_plural = 'Data'
    
    rule = models.ForeignKey(Rule)
    value = models.CharField(blank=True, max_length=1024)
    
    def __unicode__(self):
        return '%s - %s' % (value, rule)

