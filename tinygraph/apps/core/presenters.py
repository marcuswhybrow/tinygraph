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
        def __init__(self, x, y):
            self.x = int(x)
            self.y = int(y)
    
    def __init__(self, queryset):
        self.queryset = queryset
    
    def _get_data_point(self, data_instance):
        return Presenter.DataPoint(data_instance.get_timestamp() * 1000, data_instance.value)
        
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
    
    TODO This doesn't take time into account so a large gap in time between
         DataInstances generally means a large (unsightly) increase in
         difference.
         
         Some sort of time based averaging of values needs to be sorted out
         as a larger part of the system.
    """
    def __init__(self, *args, **kwargs):
        super(CounterPresenter, self).__init__(*args, **kwargs)
        self._prev_obj = None
    
    def points(self):
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