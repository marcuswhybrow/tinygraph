import datetime
import scheduler
import daemon
import sys
import logging
import logging.handlers
import time

LOG_FILENAME = '/tmp/tinygraphd.log'

# Logging stuff
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)

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
            logging.info('%s Started poll, time elapsed since last poll: %s' %(self.this_time, self.this_time - self.last_time))
        else:
            logging.info('%s Started poll' % self.this_time)
        self.last_time = self.this_time
        
        # Call the all important (overriden) poll method
        self.poll()
    
    def run(self):
        # Sheduler stuff
        my_scheduler = scheduler.Scheduler()
        
        # Get the next round second
        now = datetime.datetime.now()
        start_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
        start_time = start_time + datetime.timedelta(seconds=1)
        
        logging.info('%s Started Daemon' % now)
        
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
        print 'stopping'
        logging.info('%s Stopping Daemon' % datetime.datetime.now())
        super(PollDaemon, self).stop(*args, **kwargs)