from django.core.management.base import NoArgsCommand
from pysnmp.smi import builder, view
from data.models import DataObject, MibUpload
from pysnmp.smi.error import NoSuchObjectError
import os

class Command(NoArgsCommand):
    help = 'Creates the DataType enteries in the database, from the python representation of common MIB files created by pysnmp'
    def handle_noargs(self, **options):
        # TODO Find a way to also import OID descriptions from the MIB files,
        #      however the mibViewController doesn't seem to provide access to
        #      this.
        result = raw_input('Are you sure, this will remove existing DataObject enteries (y/N): ')
        if result.lower() != 'y':
            return
        
        print 'OK, This will take a minute or so (there\'s a lot)...'
        mibBuilder = builder.MibBuilder()
        
        # Remove the user MIB folder, preventing the sytem from owning the
        # user uploaded MIBs
        mib_paths = mibBuilder.getMibPath()
        try:
            i = mib_paths.index(os.environ['PYSNMP_MIB_DIR'])
        except (KeyError, ValueError):
            pass
        else:
            mib_paths = mib_paths[:i] + mib_paths[i+1:]
            mibBuilder.setMibPath(*mib_paths)
        
        mibBuilder.loadModules()
        mibViewController = view.MibViewController(mibBuilder)
        
        oid, label, sufix = mibViewController.getFirstNodeName()
        
        # Remove existing objects
        DataObject.objects.all().delete()
        
        # Create the "system" MibUpload instance
        system_upload, created = MibUpload.objects.get_or_create(system=True)
        
        while True:
            fields = {
                'identifier': '.'.join([str(i) for i in oid]),
                'derived_name': '.'.join([str(i) for i in label]),
            }
            
            try:
                # Ask pysnmp to clarify the what the actual oid of our guessed guessed_parent_oid is.
                guessed_parent_oid = oid[:-1]
                parent_oid, parent_label, parent_suffix = mibViewController.getNodeName(guessed_parent_oid)
            except (IndexError, NoSuchObjectError):
                pass
            else:
                parent_oid_str = '.'.join([str(i) for i in parent_oid])
                if parent_oid:
                    try:
                        fields['parent'] = DataObject.objects.get(identifier=parent_oid_str)
                    except DataObject.DoesNotExist:
                        print 'WARNING: parent DataObject with oid %s could not be found' % parent_oid_str
                        
            data_object = DataObject.objects.create(**fields)
            # Give the "system" MibUpload ownership of this DataObject
            data_object.mib_uploads.add(system_upload)
            
            try:
                oid, label, suffix = mibViewController.getNextNodeName(oid)
            except NoSuchObjectError:
                break