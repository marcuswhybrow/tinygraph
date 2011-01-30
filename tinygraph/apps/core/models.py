from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.conf import settings
from pysnmp.smi import builder, view
import subprocess
import os

class DataObjectManager(models.Manager):
    def root_only(self):
        return DataObject.objects.filter(parent=None)

class DataObject(models.Model):
    """A piece of data retrievable via a protocol from a host"""
    
    identifier = models.CharField(max_length=255, db_index=True)
    derived_name = models.CharField(blank=True, max_length=255)
    user_given_name = models.CharField(blank=True, max_length=255)
    parent = models.ForeignKey('DataObject', null=True, blank=True, db_index=True, related_name='children')
    
    objects = DataObjectManager()
    
    def __unicode__(self):
        return self.user_given_name or self.derived_name or self.identifier

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
    oid = models.CharField(max_length=100)
    file = models.FileField(upload_to='mibs')
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.file.name
    
    def save(self, *args, **kwargs):
        # TODO move this blocking stuff out of the save method and into some
        #      sort of event queue, or separate phase.
        
        # # Check to see if the OID for this MIB is already in the database
        # try:
        #     DataObject.objects.get(identifier=self.oid)
        # except DataObject.DoesNotExist:
        #     super(MibUpload, self).save(*args, **kwargs)
        # else:
        #     # This Mib is already in the database, abort this process
        #     
        #     # TODO Provide the user with some sort of notification
        #     return
        
        # Run the pysnmp MIB conversion
        path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        file_name, file_extention = os.path.splitext(os.path.basename(self.file.name))
        output_file = os.path.join(settings.MIB_ROOT, '%s.py' % file_name)
        subprocess.call(['build-pysnmp-mib', '-o', output_file, path])
        
        # This nearly works!:
        
        # # The database does not yet have this MIB, add it.
        #         uploaded_oid = tuple([int(s) for s in self.oid.split('.')])
        #         
        #         mibBuilder = builder.MibBuilder().loadModules()
        #         mibViewController = view.MibViewController(mibBuilder)
        #         oid, label, suffix = mibViewController.getNodeName(uploaded_oid)
        #         
        #         while True:
        #             fields = {
        #                 'identifier': '.'.join([str(i) for i in oid]),
        #                 'derived_name': '.'.join([str(i) for i in label]),
        #             }
        #             
        #             # Attempt to find the parent
        #             try:
        #                 # Ask pysnmp to clarify the what the actual oid of our guessed
        #                 # guessed_parent_oid is.
        #                 guessed_parent_oid = oid[:-1]
        #                 parent_oid, parent_label, parent_suffix = mibViewController.getNodeName(guessed_parent_oid)
        #             except (IndexError, NoSuchObjectError):
        #                 # This the root node, I think python syntax prevents an IndexError here actually
        #                 pass
        #             else:
        #                 parent_oid_str = '.'.join([str(i) for i in parent_oid])
        #                 if parent_oid:
        #                     try:
        #                         fields['parent'] = DataObject.objects.get(identifier=parent_oid_str)
        #                     except DataObject.DoesNotExist:
        #                         # TODO this should be a logging of some king really
        #                         pass
        #                         
        #             # Create it
        #             DataObject.objects.create(**fields)
        #             
        #             # Get the next 
        #             try:
        #                 oid, label, suffix = mibViewController.getNextNodeName(oid)
        #             except NoSuchObjectError:
        #                 break
        #             
        #             if oid[:len(uploaded_oid)] != uploaded_oid:
        #                 # This OID after the new MIB, stop!
        #                 break