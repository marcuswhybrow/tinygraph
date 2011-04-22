from django.db import models
from pysnmp.smi import builder, view
from pysnmp.smi.error import NoSuchObjectError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from tinygraph.apps.rules.models import Rule, PackageInstance, \
    PackageInstanceMembership

import subprocess
import os
import time

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


    def save(self, *args, **kwargs):
        super(MibUpload, self).save(*args, **kwargs)

        if self.system or not self.file:
            return

        if self.file:
            # Run the pysnmp MIB conversion
            file_name = self.get_file_name()
            path = os.path.join(settings.MEDIA_ROOT, self.file.name)
            output_file = os.path.join(settings.MIB_ROOT, '%s.py' % file_name)
            subprocess.call(['build-pysnmp-mib', '-o', output_file, path])

            # Trying to load the same Mib twice results in a pysnmp.smi.error.SmiError
            try:
                view.MibViewController(builder.MibBuilder().loadModules())
            except:
                os.remove(output_file)
                self.delete()
                return

        # TODO move this blocking stuff out of the save method and into some
        #      sort of event queue, or separate phase.

        mibBuilder = builder.MibBuilder().unloadModules().loadModules(self.get_file_name())
        mibViewController = view.MibViewController(mibBuilder)

        ENTERPRISES_OID = (1,3,6,1,4,1)
        oid, label, suffix = mibViewController.getNodeName(ENTERPRISES_OID)

        while True:
            try:
                oid, label, suffix = mibViewController.getNextNodeName(oid)
            except NoSuchObjectError:
                break

            if len(oid) <= len(ENTERPRISES_OID) or oid[:6] != ENTERPRISES_OID:
                continue
            else:
                pass

            fields = {
                'identifier': '.'.join([str(i) for i in oid]),
                'derived_name': '.'.join([str(i) for i in label]),
            }

            # Attempt to find the parent
            try:
                # Ask pysnmp to clarify the what the actual oid of our guessed guessed_parent_oid is.
                guessed_parent_oid = oid[:-1]
                parent_oid, parent_label, parent_suffix = mibViewController.getNodeName(guessed_parent_oid)
            except (IndexError, NoSuchObjectError):
                pass
            else:
                if parent_oid:
                    parent_oid_str = '.'.join([str(i) for i in parent_oid])
                    try:
                        fields['parent'] = DataObject.objects.get(identifier=parent_oid_str)
                    except DataObject.DoesNotExist:
                        # TODO this should be a logging of some kind really
                        pass

            # Create it. Using get_or_create would be too unwieldy
            try:
                data_object = DataObject.objects.get(identifier=fields['identifier'])
            except DataObject.DoesNotExist:
                data_object = DataObject.objects.create(**fields)
            # Adds this MIB as an owner of this new (or existing DataObject)
            data_object.mib_uploads.add(self)

    def delete(self, *args, **kwargs):
        file_name, file_extention = os.path.splitext(os.path.basename(self.file.name))
        try:
            os.remove(os.path.join(settings.MIB_ROOT, '%s.py' % file_name))
        except OSError:
            pass

        data_objects = self.data_objects.all()
        for data_object in data_objects:
            data_object.mib_uploads.remove(self)
            if not data_object.mib_uploads.count():
                data_object.delete()

        super(MibUpload, self).delete(*args, **kwargs)