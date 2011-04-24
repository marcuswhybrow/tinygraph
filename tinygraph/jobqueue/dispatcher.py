from tinygraph.jobqueue.settings import ADDRESS, PORT
from functools import wraps
import beanstalkc
import logging

logger = logging.getLogger('tinygraph.jobqueue.dispatcher')

class Dispatcher(object):
    _beanstalk = None
    
    def __init__(self, *args, **kwargs):
        super(Dispatcher, self).__init__(*args, **kwargs)
    
    def _connected(self):
        try:
            self._beanstalk.using()
        except beanstalkc.SocketError:
            return False
        else:
            return True
    
    def _ensure_connected(self):
        if self._beanstalk is None:
            try:
                self._beanstalk = beanstalkc.Connection(host=ADDRESS, port=PORT)
            except beanstalkc.SocketError, e:
                logger.critical('Could not connect (1) to beanstalkd at %s:%s, %s' % (ADDRESS, PORT, e))
        else:
            if self._connected():
                return True
            else:
                try:
                    self._beanstalk.connect()
                except beanstalkc.SocketError, e:
                    logger.critical('Could not connect (2) to beanstalkd at %s:%s, %s' % (ADDRESS, PORT, e))
        
        return self._connected()
    
    def _put(self, tube, message):
        self._beanstalk.use(tube)
        job_id = self._beanstalk.put(message)
        logger.info('Job dispatched "%s" <- "%s"' % (tube, message))
        return job_id
    
    def dispatch_job(self, tube, message):
        """
        Use the `jobqueue` management command to start beanstalkd before 
        dispatching any jobs.
        """
        
        if self._ensure_connected():
            try:
                return self._put(tube, message)
            except beanstalkc.SocketError, e:
                # The server may be been restarted causing a socket error, we can
                # get a new socket by connecting again
                logger.warning('Retrying connection to beanstalkd at %s:%s, %s' % (ADDRESS, PORT, e))
                self._ensure_connected()
                try:
                    return self._put(tube, message)
                except beanstalkc.SocketError, e2:
                    logger.warning('Connection retry failed to beanstalkd at %s:%s, %s' % (ADDRESS, PORT, e2))
                    pass
        else:
            logger.warning('Could not dispatch job, connection not possible.')
                
        return None

dispatcher = Dispatcher()