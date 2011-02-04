from django.core.management.base import BaseCommand, CommandError
from tinygraph.tinygraphd.tinygraphd import TinyGraphDaemon

class Command(BaseCommand):
    args = '<start|stop|restart>'
    help = 'Controls the tinygraph daemon which is responsible for polling devices using SNMP.'
    
    def handle(self, *args, **options):
        if len(args) == 1:
            daemon = TinyGraphDaemon(1, '/var/run/tinygraphd.pid')
            command = args[0]
            if 'start' == command:
                daemon.start()
            elif 'stop' == command:
                daemon.stop()
            elif 'restart' == command:
                daemon.restart()
            else:
                raise CommandError('unknown command')
        else:
            raise CommandError('usage: python manage.py tinygraphd %s' % self.args)
        

