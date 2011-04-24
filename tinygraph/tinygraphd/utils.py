from tinygraph.utils import scheduler
from tinygraph.utils import daemon
import datetime
import sys
import logging
import time

from django.conf import settings

logger = logging.getLogger('tinygraph.tinygraphd.PollDaemon')

class PollDaemon(daemon.Daemon):
    
    last_time = None
    
    def __init__(self, minutes, *args, **kwargs):
        self.minutes = minutes
        super(PollDaemon, self).__init__(*args, **kwargs)
    
    def poll(self):
        raise NotImplementedError
    
    def _function(self):
        self.this_time = datetime.datetime.now()
        if self.last_time is not None:
            logger.info('Started poll, time elapsed since last poll: %s' % (self.this_time - self.last_time))
        else:
            logger.info('Started poll')
        self.last_time = self.this_time
        
        # Call the all important (overriden) poll method
        self.poll()
        logging.info('Finished poll')
    
    def run(self):
        # Sheduler stuff
        my_scheduler = scheduler.Scheduler()
        
        # Get the next round second
        now = datetime.datetime.now()
        start_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
        start_time = start_time + datetime.timedelta(seconds=1)
        
        logger.info('Started Daemon')
        
        function_task = scheduler.Task(
            'poller',
            start_time,
            scheduler.every_x_mins(self.minutes),
            self._function
        )
        function_receipt = my_scheduler.schedule_task(function_task)
        
        # Start the scheduler
        my_scheduler.start()
        my_scheduler.join()
    
    def stop(self, *args, **kwargs):
        print 'Stopping...'
        logger.info('Stopping Daemon')
        super(PollDaemon, self).stop(*args, **kwargs)
        logger.info('Stopped Daemon')
        print 'Stopped'
    
    def start(self, *args, **kwargs):
        print 'Starting...\nStarted'
        super(PollDaemon, self).start(*args, **kwargs)



def get_mib_view_controller():
    return MibViewController(MibBuilder().loadModules())