from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.conf import settings
from pysnmp.smi import builder, view
from pysnmp.smi.error import NoSuchObjectError
import subprocess
import os
import time

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

class DataObjectManager(models.Manager):
    def root_only(self):
        return DataObject.objects.filter(parent=None)

class DataObject(models.Model):
    """A piece of data retrievable via a protocol from a host"""
    
    identifier = models.CharField(max_length=255, db_index=True, unique=True)
    derived_name = models.CharField(blank=True, max_length=255)
    user_given_name = models.CharField(blank=True, max_length=255)
    parent = models.ForeignKey('DataObject', null=True, blank=True, db_index=True, related_name='children')
    mib_uploads = models.ManyToManyField('MibUpload', db_index=True, related_name='data_objects')
    
    objects = DataObjectManager()
    
    def __unicode__(self):
        return self.user_given_name or self.derived_name or self.identifier
    
    def get_identifier_tuple(self):
        return tuple([int(s) for s in self.identifier.split('.')])

class Rule(models.Model):
    """Defines that a DataObject should be recorded for a particular Device"""
    
    data_object = models.ForeignKey('DataObject', db_index=True, related_name='rules')
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
    data_object = models.ForeignKey(DataObject, db_index=True, related_name='instances')
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


class MibUpload(models.Model):
    file = models.FileField(null=True, blank=True, upload_to='mibs', db_index=True)
    system = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
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
            
            print oid, 
            if len(oid) <= len(ENTERPRISES_OID) or oid[:6] != ENTERPRISES_OID:
                print 'out of scope'
                continue
            else:
                print 'in scope'
                
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


class Package(models.Model):
    """
    A package is a group of DataObjects which a user would frequently whish to
    enable or disable in an atomic fashion.
    
    For example a package might contain all the OIDs relevant to logging
    interface statistics for an entire machine.
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, editable=False, db_index=True)
    data_objects = models.ManyToManyField(DataObject, related_name='packages')
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
        return ('core.views.package_detail', (), {
            'package_slug': self.slug,
        })

class PackageInstance(models.Model):
    device = models.ForeignKey('devices.Device', db_index=True)
    package = models.ForeignKey(Package, db_index=True)
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