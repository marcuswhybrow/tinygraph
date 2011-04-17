from django.db import models

class EventBase(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    device = models.ForeignKey('devices.Device', db_index=True, blank=True, null=True)
    
    class Meta:
        abstract = True
        ordering = ('-created',)
        
class Event(EventBase):
    message = models.CharField(blank=True, max_length=255)
    
    def __unicode__(self):
        return u'%s: %s' % (self.device, self.message)
        
class ChangeEvent(EventBase):
    data_instance = models.ForeignKey('data.DataInstance', db_index=True, related_name='events')
    
    def __unicode__(self):
        return u'%s changed in: %s' % (self.device, self.data_instance.data_object if self.data_instance else None)