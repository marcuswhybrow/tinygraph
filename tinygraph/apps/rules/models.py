from django.db import models
from django.db import IntegrityError

DATA_OBJECT_ENABLED_DEFAULT = True
DATA_OBJECT_GRAPHED_DEFAULT = False

class Rule(models.Model):
    """Defines that a DataObject should be recorded for a particular Device"""
    
    data_object = models.ForeignKey('definitions.DataObject', db_index=True, related_name='rules')
    device = models.ForeignKey('devices.Device', db_index=True, related_name='rules')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('data_object', 'device')
    
    def __unicode__(self):
        return '%s - %s' % (self.data_object, self.device)

class PackageRule(Rule):
    package_instance_membership = models.OneToOneField('rules.PackageInstanceMembership', db_index=True, related_name='rule')
    rule = models.OneToOneField('rules.Rule', parent_link=True)
    
    class Meta:
        unique_together = ('rule', 'package_instance_membership')

class PackageInstanceMembership(models.Model):
    """
    This many to many through model allows a package instance to specify
    whether or not a particular DataObject should be enabled (collecting
    data) and additionly should it be graphed.
    
    If a record is not created for a particular DataObject (via its
    PackageMembership) then the PackageInstance must assume the defaults
    defined at the top of this file.
    """
    
    package_instance = models.ForeignKey('rules.PackageInstance', related_name='memberships')
    package_membership = models.ForeignKey('definitions.PackageMembership', related_name='memberships')
    enabled = models.BooleanField(default=DATA_OBJECT_ENABLED_DEFAULT)
    graphed = models.BooleanField(default=DATA_OBJECT_GRAPHED_DEFAULT)
    
    class Meta:
        unique_together = ('package_instance', 'package_membership')

class PackageInstance(models.Model):
    device = models.ForeignKey('devices.Device', db_index=True)
    package = models.ForeignKey('definitions.Package', db_index=True, related_name='instances')
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=False)
    data_objects = models.ManyToManyField('definitions.PackageMembership', through='rules.PackageInstanceMembership', related_name='configured_memberships')
    
    class Meta:
        unique_together = ('device', 'package')
    
    def save(self, *args, **kwargs):
        super(PackageInstance, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return '%s for %s' % (self.package, self.device)