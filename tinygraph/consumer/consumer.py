from tinygraph.utils import daemon
from django.conf import settings
import beanstalkc
import logging
import logging.handlers

HOST = getattr(settings, 'BEANSTALK_HOST', 'localhost')
PORT = getattr(settings, 'BEANSTALK_PORT', 11300)
LOG_FILENAME = getattr(settings, 'CONSUMER_LOG_FILENAME', '/var/log/consumerd.log')

# Logging stuff
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConsumerDaemon(daemon.Daemon):
    beanstalk = None
    
    def run(self):
        try:
            self.beanstalk = beanstalkc.Connection(host=HOST, port=PORT)
        except:
            logging.error('Could not connect to beanstalkd at %s:%s' % (HOST, PORT))
        else:
            if self.beanstalk:
                # Ignore the default tube
                self.beanstalk.ignore('default')
            
                # Watch some specific tubes to consume
                self.beanstalk.watch('graph')
                self.beanstalk.watch('analysis')
            
                # Start consuming jobs
                while True:
                    try:
                        job = self.beanstalk.reserve()
                    except beanstalkc.DeadlineSoon:
                        # Not sure what this exception means with the system
                        continue
                    else:
                        # Process the job
                        logging.info('Finished Job, tube: %s, message: %s' % (job.stats()['tube'], job.body))
        
                        # Remove the job from the queue once processed
                        job.delete()
    
    def stop(self, *args, **kwargs):
        # Close the connection to the beanstalk server
        if self.beanstalk:
            self.beanstalk.close()
        super(ConsumerDaemon, self).stop(*args, **kwargs)
    
    def start(self, *args, **kwargs):
        super(ConsumerDaemon, self).start(*args, **kwargs)