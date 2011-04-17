from django.db import models

EVENT_TYPES = (
    # ('d', 'Debug'),
    # ('i', 'Info'),
    ('c', 'Change in Value'),
    # ('a', 'Alert'),
)

class Event(models.Model):
    """
    Events may be logged upon collecting new data instances for a device. For
    example if a non-incrementing value changes (i.e. one that is not
    constantly increasing) an event should be logged to mark the change in
    value.
    """
    
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    event_type = models.CharField(max_length=1, choices=EVENT_TYPES, db_index=True)
    device = models.ForeignKey('devices.Device', db_index=True, related_name='events', blank=True, null=True)
    data_instance = models.ForeignKey('data.DataInstance', db_index=True, related_name='events', blank=True, null=True)
    
    def __unicode__(self):
        return u'%s for %s in %s' % (self.get_event_type_display(), self.device, self.data_instance.data_object if self.data_instance else None)