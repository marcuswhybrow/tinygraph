from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.conf import settings
from pysnmp.smi import builder, view
from pysnmp.smi.error import NoSuchObjectError
import subprocess
import os

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
    
    # def delete(self, mib_upload=None, *args, **kwargs):
    #     if mib_upload is not None:
    #         count = self.mib_uploads.filter(pk=mib_upload.pk).count()
    #         if count:
    #             self.mib_uploads.remove(mib_upload)
    #             if count - 1:
    #                 # If there are still other MIBs which need this DataObject
    #                 # then do not delete it.
    #                 return
    #         else:
    #             # The MibUpload has no right to delete this DataObject since
    #             # it does not have ownership
    #             return
    #         # Cascade delete the children (with the mib_upload kwarg)
    #         for data_object in self.children.all():
    #             data_object.delete(mib_upload=mib_upload)
    #     super(DataObject, self).delete(*args, **kwargs)

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
        self.full_clean()
        super(MibUpload, self).save(*args, **kwargs)
        
        if self.file is None or self.file.name is None:
            return
        
        # TODO move this blocking stuff out of the save method and into some
        #      sort of event queue, or separate phase.
        
        # Run the pysnmp MIB conversion
        path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        file_name = self.get_file_name()
        output_file = os.path.join(settings.MIB_ROOT, '%s.py' % file_name)
        subprocess.call(['build-pysnmp-mib', '-o', output_file, path])
        
        
        mibBuilder = builder.MibBuilder().unloadModules().loadModules(file_name)
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
        os.remove(os.path.join(settings.MIB_ROOT, '%s.py' % file_name))
        
        # TODO Remove stuff from the database, without remove enteries in use
        #      by remaining MIBs
        
        data_objects = self.data_objects.all()
        for data_object in data_objects:
            data_object.mib_uploads.remove(self)
            if not data_object.mib_uploads.count():
                data_object.delete()
        
        super(MibUpload, self).delete(*args, **kwargs)