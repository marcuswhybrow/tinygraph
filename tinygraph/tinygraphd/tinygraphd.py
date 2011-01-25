import datetime
import scheduler
import daemon
import sys
import logging
import logging.handlers
import time

LOG_FILENAME = '/Users/marcus/Desktop/tinygraphd.log'

class TinyGraphDaemon(daemon.Daemon):
    
    last_time = None
    
    def _function(self):
        self.this_time = datetime.datetime.now()
        if self.last_time is not None:
            logging.info('time: %s difference: %s' %(self.this_time, self.this_time - self.last_time))
        else:
            logging.info('time: %s' % self.this_time)
        self.last_time = self.this_time
    
    def run(self):
        # Sheduler stuff
        my_scheduler = scheduler.Scheduler()
        
        # Get the next round second
        now = datetime.datetime.now()
        start_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
        start_time = start_time + datetime.timedelta(seconds=1)
        
        # Logging stuff
        logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)
        
        logging.info('start time: %s' % start_time)
        
        function_task = scheduler.Task(
            'task',
            start_time,
            scheduler.every_x_secs(1),
            self._function
        )
        function_receipt = my_scheduler.schedule_task(function_task)
        
        # Start the scheduler
        my_scheduler.start()
        my_scheduler.join()