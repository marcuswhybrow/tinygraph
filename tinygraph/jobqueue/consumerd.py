from tinygraph.utils import daemon
from django.conf import settings
from tinygraph.jobqueue.settings import ADDRESS, PORT, JOB_TYPES
from tinygraph.jobqueue import consumers
import beanstalkc
import logging

logger = logging.getLogger('tinygraph.jobqueue.consumerd')

class ConsumerDaemon(daemon.Daemon):
    beanstalk = None
    
    def run(self):
        try:
            self.beanstalk = beanstalkc.Connection(host=ADDRESS, port=PORT)
        except:
            logger.error('Could not connect to beanstalkd at %s:%s' % (ADDRESS, PORT))
        else:
            if self.beanstalk:
                # Watch some specific tubes to consume
                for tube in JOB_TYPES:
                    logger.debug('listening on tube: %s' % tube)
                    self.beanstalk.watch(tube)
            
                # Start consuming jobs
                while True:
                    logger.debug('waiting for job...')
                    try:
                        job = self.beanstalk.reserve()
                    except beanstalkc.DeadlineSoon:
                        # Not sure what this exception means
                        logger.info('Deadline Soon')
                        continue
                    else:
                        tube = job.stats()['tube']
                        message = job.body
                        
                        method = getattr(consumers, '%s_consumer' % tube, None)
                        if method:
                            method(job)
                            logger.info('Job consumed: "%s" <- "%s"' % (tube, message))
                        else:
                            logger.info('Job does not have a consumer: "%s" <- "%s"' % (tube, message))
                            job.delete()
                
                logger.debug('Exiting job wait loop.')
            else:
                logger.debug('Connection to beanstalk not found.')
                        
    
    def stop(self, *args, **kwargs):
        # Close the connection to the beanstalk server
        logger.info('Stopped')
        if self.beanstalk:
            self.beanstalk.close()
        super(ConsumerDaemon, self).stop(*args, **kwargs)
    
    def start(self, *args, **kwargs):
        logger.info('Started')
        super(ConsumerDaemon, self).start(*args, **kwargs)
    