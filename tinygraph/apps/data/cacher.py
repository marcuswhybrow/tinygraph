from django.core.cache import cache
from tinygraph.apps.data.models import DataInstance
import logging

PROJECT_KEY = 'tinygraph'
DATA_INSTANCE_KEY = 'data_instances'

logger = logging.getLogger('tinygraph.data.cacher')

def _get_cache_key(device_slug, derived_name, suffix):
    return '%s:%s:%s:%s[%s]' % (PROJECT_KEY, DATA_INSTANCE_KEY, device_slug, 
        derived_name, suffix)

class Cacher(object):
    def _set(self, key, value):
        cache.set(key, value, timeout=86400)
        logger.info('"%s" set as "%s"' % (key, value))
    
    def __setitem__(self, key, value):
        cache_key = _get_cache_key(*key)
        self._set(cache_key, value)
    
    def __getitem__(self, key):
        cache_key = _get_cache_key(*key)
        
        logger.info('"%s" got' % cache_key)
        
        # Attempt to get the value from cache
        value = cache.get(cache_key)
        
        # If the value was not found in the cache then try the database
        if value is None:
            device_slug, derived_name, suffix = key
            try:
                value = DataInstance.objects.filter(
                    rule__device__slug=device_slug, 
                    data_object__derived_name=derived_name, 
                    suffix=suffix
                ).values_list('value').latest()[0]
            except DataInstance.DoesNotExist:
                pass
            else:
                # If a value was found in the database, set that as the value
                # in the cache
                self._set(cache_key, value)

        return value

cacher = Cacher()