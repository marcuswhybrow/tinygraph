from django.dispatch import receiver
from django.db.models.signals import post_save
from tinygraph.apps.data.cacher import cacher
from tinygraph.apps.data.models import DataInstance
import logging

logger = logging.getLogger('tinygraph.data.receivers')

@receiver(post_save, sender=DataInstance)
def update_caches(sender, instance=None, created=None, **kwargs):
    if instance and created:
        # Update the DataObject's value_type if it doesnt know it yet
        if instance.data_object.value_type is None:
            instance.data_object.value_type = instance.value_type
            instance.data_object.save()
        
        # If this is a non-incremental data type, then store this latest
        # version in the cache
        if instance.value_type != 'counter':
            cache_key = (
                instance.rule.device.slug,
                instance.data_object.derived_name,
                instance.suffix
            )
            
            cacher[cache_key] = (instance.value, instance.created)