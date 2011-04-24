from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from tinygraph.apps.rules.models import Rule, PackageInstance, \
    PackageInstanceMembership
from tinygraph.apps.data.settings import DATA_VALUE_TYPES
import os

class DataObjectManager(models.Manager):
    def root_only(self):
        return DataObject.objects.filter(parent=None)

class DataObject(models.Model):
    """A piece of data retrievable via a protocol from a host"""
    
    identifier = models.CharField(max_length=255, db_index=True, unique=True)
    derived_name = models.CharField(blank=True, max_length=255, db_index=True)
    user_given_name = models.CharField(blank=True, max_length=255)
    parent = models.ForeignKey('DataObject', null=True, blank=True, db_index=True, related_name='children')
    mib_uploads = models.ManyToManyField('MibUpload', db_index=True, related_name='data_objects')
    # This field is not knowable on create due to the limitations of pysnmp
    # library, instead it is updated when a DataInstance is created.
    value_type = models.CharField(max_length=100, choices=DATA_VALUE_TYPES, null=True, blank=True)
    
    objects = DataObjectManager()
    
    def __unicode__(self):
        return self.user_given_name or self.derived_name or self.identifier
    
    def get_identifier_tuple(self):
        return tuple([int(s) for s in self.identifier.split('.')])

class PackageMembership(models.Model):
    """
    A PackageMembership is created for each DataObject which contained within
    a Package.
    
    When saved this model 
    """
    package = models.ForeignKey('definitions.Package', db_index=True, related_name='memberships')
    data_object = models.ForeignKey('definitions.DataObject', db_index=True, related_name='memberships')
    
    class Meta:
        unique_together = ('package', 'data_object')
    
    __unicode__ = lambda self: u'%s <-> %s' % (self.package, self.data_object)


class Package(models.Model):
    """
    A package is a group of DataObjects which a user would frequently whish to
    enable or disable in an atomic fashion.

    For example a package might contain all the OIDs relevant to logging
    interface statistics for an entire machine.
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, editable=False, db_index=True)
    data_objects = models.ManyToManyField('DataObject', through='definitions.PackageMembership', related_name='packages')
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    editable = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.title))
        super(Package, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('definitions:package_detail', (), {
            'package_slug': self.slug,
        })
                    

class MibUpload(models.Model):
    file = models.FileField(null=True, blank=True, upload_to='mibs', db_index=True)
    system = models.BooleanField(default=False)

    def __unicode__(self):
        return self.get_file_name() if not self.system else 'System'

    def get_file_name(self):
        if self.file is not None:
            return os.path.splitext(os.path.basename(self.file.name))[0]
        return None

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.system and MibUpload.objects.filter(system=True).count():
            # If there already exists (hopefully only) one system instance
            raise ValidationError('The "system" MibUpload already exists.')
        if self.system and self.file != None:
            # If this is the system instance and a file is also specified
            raise ValidationError('The "system" MibUpload can not have an associated MIB file.')
        if not self.system and not self.file:
            # If this is NOT the system instance and a file is NOT specified
            raise ValidationError('You must provide a MIB file.')