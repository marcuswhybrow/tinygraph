from tinygraph.apps.core.cacher import BaseCacher
from tinygraph.apps.data.models import DataInstance
import logging


DATA_INSTANCE_KEY = 'data_instances'

logger = logging.getLogger('tinygraph.data.cacher')

class DataInstanceCacher(BaseCacher):
    def get_cache_key(self, key):
        device_slug, derived_name, suffix = key
        project_Key = super(DataInstanceCacher, self).get_cache_key(key)
        return '%s:%s:%s:%s[%s]' % (project_Key, DATA_INSTANCE_KEY, device_slug, 
            derived_name, suffix)
    
    def find_item(self, key):
        logger.debug('finding DataInstance item %s' % str(key))
        device_slug, derived_name, suffix = key
        try:
            value = DataInstance.objects.filter(
                rule__device__slug=device_slug, 
                data_object__derived_name=derived_name, 
                suffix=suffix
            ).values_list('value', 'created').latest()
        except DataInstance.DoesNotExist:
            return (None, None)
        else:
            # If a value was found in the database, set that as the value
            # in the cache
            self._set(self.get_cache_key(key), value)
            return value

cacher = DataInstanceCacher()