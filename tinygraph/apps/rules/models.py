from django.db import models

class Rule(models.Model):
    """Defines that a DataObject should be recorded for a particular Device"""
    
    data_object = models.ForeignKey('definitions.DataObject', db_index=True, related_name='rules')
    device = models.ForeignKey('devices.Device', db_index=True, related_name='rules')
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    
    package_instance = models.ForeignKey('PackageInstance', db_index=True, null=True, blank=True, related_name='rules')
    
    class Meta:
        unique_together = ('data_object', 'device', 'package_instance')
    
    def __unicode__(self):
        return '%s - %s' % (self.data_object, self.device)

class PackageInstance(models.Model):
    device = models.ForeignKey('devices.Device', db_index=True)
    package = models.ForeignKey('definitions.Package', db_index=True)
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