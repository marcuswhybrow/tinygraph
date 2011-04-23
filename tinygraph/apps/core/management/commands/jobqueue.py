from django.core.management.base import BaseCommand, CommandError
from tinygraph.jobqueue.consumer import ConsumerDaemon
from django.conf import settings
import subprocess

ADDRESS = getattr(settings, 'BEANSTALK_ADDRESS', '127.0.0.1')
PORT = getattr(settings, 'BEANSTALK_PORT', 11300)

class Command(BaseCommand):
    args = '<start|stop|restart>'
    help = 'Controls the consumer daemon which is responsible for consuming queue jobs.'
    
    def handle(self, *args, **options):
        if len(args) == 1:
            daemon = ConsumerDaemon('/tmp/tinygraph-jobqueue-consumer.pid')
            command = args[0]
            if 'start' == command:
                subprocess.call('beanstalkd -d -l %s -p %d' % (ADDRESS, PORT), shell=True)
                daemon.start()
            elif 'stop' == command:
                daemon.stop()
                subprocess.call('killall beanstalkd', shell=True)
            elif 'restart' == command:
                daemon.restart()
            else:
                raise CommandError('unknown command')
        else:
            raise CommandError('usage: python manage.py tinygraphd %s' % self.args)
        

