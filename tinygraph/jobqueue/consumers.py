from functools import wraps
from tinygraph.apps.definitions.models import MibUpload, DataObject
from pysnmp.smi import view, builder
from pysnmp.smi.error import NoSuchObjectError
from django.conf import settings
import beanstalkc
import logging
import subprocess
import os

logger = logging.getLogger('tinygraph.jobqueue.consumers')

def consumer(f):
    def wrapper(job):
        try:
            result = f(job)
        except Exception, e:
            logger.critical('consumer raised an error: %s' % e)
            job.release()
            return None
        if result == False:
            job.release()
        else:
            job.delete()
        return result
    return wraps(f)(wrapper)

# -- Job consumers --

# Returning False from an @consumer decorated method releases the job,
# returning True or None (i.e. not returning anything), deletes the job.

@consumer
def mib_integration_consumer(job):
    """
    When you upload a new .mib file for use within the system, this job
    converts it to a pysnmp .py file and and then adds each new data
    objects into the hierarchy of data objects which TinyGraph maintains.
    """
    
    pk = job.body
    
    try:
        mib_upload = MibUpload.objects.get(pk=pk)
    except MibUpload.DoesNotExist, e:
        return False

    if mib_upload.system or not mib_upload.file:
        return

    if mib_upload.file:
        # Run the pysnmp MIB conversion
        file_name = mib_upload.get_file_name()
        path = os.path.join(settings.MEDIA_ROOT, mib_upload.file.name)
        output_file = os.path.join(settings.MIB_ROOT, '%s.py' % file_name)
        subprocess.call(['build-pysnmp-mib', '-o', output_file, path])

        # Trying to load the same Mib twice results in a pysnmp.smi.error.SmiError
        try:
            view.MibViewController(builder.MibBuilder().loadModules())
        except:
            os.remove(output_file)
            mib_upload.delete()
            return

    mibBuilder = builder.MibBuilder().unloadModules().loadModules(mib_upload.get_file_name())
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
        data_object.mib_uploads.add(mib_upload)

@consumer
def mib_disintegration_consumer(job):
    """
    When you delete a .mib file from TinyGraph the data objects added to 
    the system must be removed to maintain integrity. And also the pysnmp
    .py file must be removed so it is not included in the future.
    """
    
    pk = job.body

    try:
        mib_upload = MibUpload.objects.get(pk=pk)
    except MibUpload.DoesNotExist:
        return

    file_name, file_extention = os.path.splitext(os.path.basename(mib_upload.file.name))
    try:
        os.remove(os.path.join(settings.MIB_ROOT, '%s.py' % file_name))
    except OSError:
        pass

    data_objects = mib_upload.data_objects.all()
    for data_object in data_objects:
        data_object.mib_uploads.remove(mib_upload)
        if not data_object.mib_uploads.count():
            data_object.delete()