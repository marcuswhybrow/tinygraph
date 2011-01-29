from django.core.management.base import NoArgsCommand
from pysnmp.smi import builder, view
from tinygraph.apps.core.models import DataObject
from pysnmp.smi.error import NoSuchObjectError

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
        mibBuilder = builder.MibBuilder().loadModules()
        mibViewController = view.MibViewController(mibBuilder)
        
        oid, label, sufix = mibViewController.getFirstNodeName()
        
        # Remove existing objects
        DataObject.objects.all().delete()
        
        while True:
            DataObject.objects.create(
                identifier='.'.join([str(i) for i in oid]),
                derived_name='.'.join([str(i) for i in label])
            )
            try:
                oid, label, suffix = mibViewController.getNextNodeName(oid)
            except NoSuchObjectError:
                break