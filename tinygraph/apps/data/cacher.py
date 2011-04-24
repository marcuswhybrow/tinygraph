from django.core.cache import cache
from tinygraph.apps.data.models import DataInstance
import logging
import hashlib

PROJECT_KEY = 'tinygraph'
DATA_INSTANCE_KEY = 'data_instances'

logger = logging.getLogger('tinygraph.data.cacher')

def _get_cache_key(device_slug, derived_name, suffix):
    return '%s:%s:%s:%s[%s]' % (PROJECT_KEY, DATA_INSTANCE_KEY, device_slug, 
        derived_name, suffix)

def _hash(key):
    """
    Hashes a key, useful because MemCached ignores keys with whitespace or
    those longer than 250 characters
    """
    m = hashlib.md5()
    m.update(key)
    return m.hexdigest()

class Cacher(object):
    def _set(self, key, value):
        cache.set(_hash(key), value, timeout=86400)
    
    def __setitem__(self, key, value):
        cache_key = _get_cache_key(*key)
        self._set(cache_key, value)
    
    def __getitem__(self, key):
        cache_key = _get_cache_key(*key)
        
        # Attempt to get the value from cache
        value = cache.get(_hash(cache_key))
        
        # If the value was not found in the cache then try the database
        if value is None:
            device_slug, derived_name, suffix = key
            try:
                value = DataInstance.objects.filter(
                    rule__device__slug=device_slug, 
                    data_object__derived_name=derived_name, 
                    suffix=suffix
                ).values_list('value', 'created').latest()
            except DataInstance.DoesNotExist:
                pass
            else:
                # If a value was found in the database, set that as the value
                # in the cache
                self._set(cache_key, value)

        return value or (None, None)

cacher = Cacher()