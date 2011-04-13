import datetime
from data.utils import datetime_to_timestamp

class Presenter(object):
    """
    This class provides a translation between DataInstances in the database
    and Presenter.DataPoint objects which contain just an x and y value.
    
    This makes the template code much simpler and provides a place to do any
    complex logic by subclassing for different ways of presenting data.
    
    This base class simply converts each DataInstance into a DataPoint.
    """
    
    class DataPoint(object):
        """Used in the tempalte for graphing data points"""
        def __init__(self, x=None, y=None):
            if x is not None:
                self.x = int(x)
            if y is not None:
                self.y = int(y)
                
            if x is None and y is None:
                self.null = True
    
    class NullDataPoint(DataPoint):
        def __init__(self, x=None, *args, **kwargs):
            super(Presenter.NullDataPoint, self).__init__(x)
    
    def __init__(self, queryset, granularity=None, start_time=None, end_time=None):
        # A queryset assumed to contain only DataInstance instances
        self.queryset = queryset
        # A datetime.timedelta which specifies the interval between the ouput
        # DataPoint instances
        self.granularity = granularity
        # A datetime.datetime which specifies the time of the first DataPoint
        # output.
        self.start_time = start_time
        # A datetime.datetime which specifices the that the no DataPoint can
        # include DataInstance instances greater than this time.
        self.end_time = end_time
        
        self._cache = None
        
        # If start_time and end_time are provided, then the queryset should be
        # refined in order to include only DataInstances within range
        #
        # This does not cause another database hit as the queryset has not
        # been evaluated yet.
        if self.start_time is not None or self.end_time is not None:
            fields = {}
            if self.start_time is not None:
                fields['created__gte'] = self.start_time
            if self.end_time is not None:
                fields['created__lt'] = self.end_time
            self.queryset = self.queryset.filter(**fields)
        
        # If a granularity is specified then output DataPoint instances will
        # be at a regular interval starting from the start_time value.
        if self.granularity is not None:
            # evaluate the queryset
            if self.start_time is None and len(self.instances) > 0:
                # Get the minute that the oldest time was recorded at
                t = self.instances[0].created
                self.start_time = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute)
                
            if self.end_time is None and len(self.instances) > 0:
                t = self.instances[len(self.instances)-1].created
                self.end_time = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute)
                self.end_time += datetime.timedelta(minutes=1)
    
    @property
    def instances(self):
        if self._cache is None:
            self._cache = list(self.queryset)
        return self._cache
    
    def _get_data_point(self, data_instance):
        return Presenter.DataPoint(datetime_to_timestamp(data_instance.created) * 1000, data_instance.value)
    
    def _get_intervals(self, start_time, interval, end_time):
        t = start_time
        while True:
            start_time = t
            t += interval
            yield start_time, t
            if t >= end_time:
                break
        
    def points(self):
        for obj in self.queryset:
            yield self._get_data_point(obj)

class CounterPresenter(Presenter):
    """
    A counter SNMP type returns an increasingly larger value for each poll,
    whcih would ordinarily create a graph with a constantly positive gradient.
    
    In order to compare data points on a graph more effectively, subtracting
    the previous DataPoint's value will provide the amount of increase on a
    counter rather than its absolute value.
    
    The CounterPresenter will not yield the oldest DataInstance as a DataPoint
    since it does not have a previous DataInstance from which to subtract a
    value.
    """
    def __init__(self, *args, **kwargs):
        super(CounterPresenter, self).__init__(*args, **kwargs)
        self._prev_obj = None
    
    def points(self):
        if len(self.instances) <= 0:
            return
            
        if self.granularity:
            prev_average = None
            prev_period = None
            for start_time, end_time in self._get_intervals(self.start_time, self.granularity, self.end_time):
                
                def data_instance_filter(item):
                    if item.created < start_time or item.created >= end_time:
                        return False
                    return True
                instances = filter(data_instance_filter, self.instances)
                
                if len(instances) > 0:
                    total = 0
                    for instance in instances:
                        total += int(instance.value)
                    average = float(total) / len(instances)
                    if prev_period is not None:
                        delta = end_time - prev_period['end_time']
                        delta_secs = delta.days * 86400 + delta.seconds
                        value = (average - prev_period['average']) / delta_secs
                        prev_period = {
                            'start_time': start_time,
                            'end_time': end_time,
                            'average': average,
                        }
                        yield Presenter.DataPoint(datetime_to_timestamp(start_time)*1000, value)
                    else:
                        prev_period = {
                            'start_time': start_time,
                            'end_time': end_time,
                            'average': average,
                        }
                        continue
                else:
                    yield Presenter.NullDataPoint()
        else:
            for obj in self.queryset:
                if self._prev_obj is None:
                    # This is the first DataInstance, do NOT create a DataPoint
                    self._prev_obj = obj
                    continue
            
                # For every other instance, yield a DataPoint with the previous
                # DataInstances value subtracted.
                data_point = self._get_data_point(obj)
                prev_data_point = self._get_data_point(self._prev_obj)
                data_point.y -= prev_data_point.y
                self._prev_obj = obj
                yield data_point