from django.core.management.base import BaseCommand, CommandError
from tinygraph.jobqueue.consumerd import ConsumerDaemon
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
                # -b writes all jobs to a bin so they can be resumed if the
                # power is cut
                # -d detaches the process as a daemon
                # -l is the address to listen on
                # -p is the port to listen on
                # run `beanstalkd -h` on the command for more options
                print 'Starting beanstalkd...'
                subprocess.call('beanstalkd -d -l %s -p %d' % (ADDRESS, PORT), shell=True)
                print 'Starting consumer...'
                daemon.start()
                print 'Everything started.'
            elif 'stop' == command:
                print 'Stopping consumer...'
                daemon.stop()
                print 'Stopping beanstalkd...'
                subprocess.call('killall beanstalkd', shell=True)
                print 'Everything stopped.'
            elif 'restart' == command:
                subprocess.call('killall beanstalkd', shell=True)
                subprocess.call('beanstalkd -d -l %s -p %d' % (ADDRESS, PORT), shell=True)
                daemon.restart()
            else:
                raise CommandError('unknown command')
        else:
            raise CommandError('usage: python manage.py tinygraphd %s' % self.args)
        

