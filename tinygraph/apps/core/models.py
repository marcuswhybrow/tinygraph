from django.db import models

DATA_VALUE_TYPES = (
    # Primitive ASN.1 Types
    ('integer', 'Integer'),
    ('bit_string', 'Bit String'),
    ('octet_string', 'Octet String'),
    ('null', 'Null'),
    ('object_identifier', 'Object Identifier'),
    
    # Constructed ASN.1 Types
    ('sequence', 'Sequence'),
    
    # Primitive SNMP Application Types
    ('ip_address', 'IP Address'),
    ('counter', 'Counter'),
    ('gauge', 'Gauge'),
    ('time_ticks', 'Time Ticks'),
    ('opaque', 'Opaque'),
    ('nsap_address', 'Nsap Address'),
)

class Rule(models.Model):
    """Defines that a DataObject should be recorded for a particular Device"""
    
    data_object = models.ForeignKey('data.DataObject', db_index=True, related_name='rules')
    device = models.ForeignKey('devices.Device', db_index=True, related_name='rules')
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    
    package_instance = models.ForeignKey('PackageInstance', db_index=True, null=True, blank=True, related_name='rules')
    
    class Meta:
        unique_together = ('data_object', 'device', 'package_instance')
    
    def __unicode__(self):
        return '%s - %s' % (self.data_object, self.device)


class DataInstance(models.Model):
    """Data collected for a Rule regarding a DataObject"""
    
    # The Rule this DataInstance was created by
    # A Rule does reference a DataObject however many DataInstances may be
    # found under a particular DataObject on the polled device
    rule = models.ForeignKey(Rule, db_index=True, related_name='instances')
    # The closest match in the systems representation of DataObjects which
    # this data instance matches against
    data_object = models.ForeignKey('data.DataObject', db_index=True, related_name='instances')
    # The remaineder of the match against the database representation. This is
    # often an index of an array of values for a particular OID on the polled
    # device, or can incldue further unknwon hierarchy that is not held in the
    # system representation.
    suffix = models.CharField(max_length=255, db_index=True)
    # The value for this DataInstance
    value = models.CharField(blank=True, max_length=1024)
    # The time this DataIntance was created (very critical)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    
    value_type = models.CharField(max_length=100, choices=DATA_VALUE_TYPES)
    
    class Meta:
        get_latest_by = 'created'
    
    def __unicode__(self):
        return '%s %s[%s] = %s' % (self.rule.device, self.data_object, self.suffix, self.value)

class PackageInstance(models.Model):
    device = models.ForeignKey('devices.Device', db_index=True)
    package = models.ForeignKey('data.Package', db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('device', 'package')
    
    def save(self, *args, **kwargs):
        super(PackageInstance, self).save(*args, **kwargs)
        for data_object in self.package.data_objects.all():
            try:
                rule = Rule.objects.get(device=self.device, data_object=data_object, package_instance=self)
            except Rule.DoesNotExist:
                rule = Rule.objects.create(device=self.device, data_object=data_object, package_instance=self, enabled=self.enabled)
            else:
                if rule.enabled != self.enabled:
                    rule.enabled = self.enabled
                    rule.save()
    
    def __unicode__(self):
        return '%s for %s' % (self.package, self.device)