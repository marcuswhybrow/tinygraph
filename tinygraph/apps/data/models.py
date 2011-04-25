from django.db import models
from django.dispatch import receiver
from tinygraph.apps.data.settings import DATA_VALUE_TYPES

class DataInstance(models.Model):
    """Data collected for a Rule regarding a DataObject"""
    
    # The Rule this DataInstance was created by
    # A Rule does reference a DataObject however many DataInstances may be
    # found under a particular DataObject on the polled device
    rule = models.ForeignKey('rules.Rule', db_index=True, 
        related_name='instances')
    # The closest match in the systems representation of DataObjects which
    # this data instance matches against
    data_object = models.ForeignKey('definitions.DataObject', db_index=True, 
        related_name='instances')
    # The remaineder of the match against the database representation. This is
    # often an index of an array of values for a particular OID on the polled
    # device, or can incldue further unknwon hierarchy that is not held in the
    # system representation.
    suffix = models.CharField(max_length=255, db_index=True)
    # The value for this DataInstance
    value = models.CharField(blank=True, max_length=1024)
    # The time this DataIntance was created (very critical)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    
    value_type = models.CharField(max_length=100, choices=DATA_VALUE_TYPES)
    
    poll = models.ForeignKey('data.Poll', related_name='instances')
    
    class Meta:
        get_latest_by = 'created'
    
    def __unicode__(self):
        return u'%s %s[%s] = %s' % (self.rule.device, self.data_object, 
            self.suffix, self.value)

class Poll(models.Model):
    """A poll for DataInstance objects to belong to."""
    
    start = models.DateTimeField(null=True, blank=True)
    stop = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        get_latest_by = 'start'
    
    def __unicode__(self):
        return u'Poll, started %s, ended %s' % (self.start, self.stop)