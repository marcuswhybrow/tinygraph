from django.core.cache import cache
import hashlib

PROJECT_KEY = 'tinygraph'

def _hash(key):
    """
    Hashes a key, useful because MemCached ignores keys with whitespace or
    those longer than 250 characters
    """
    m = hashlib.md5()
    m.update(key)
    return m.hexdigest()

class BaseCacher(object):
    def _set(self, key, value):
        cache.set(_hash(key), value, timeout=86400)
    
    def get_cache_key(self, key):
        """Implement this to return a unique cache key for each key"""
        return PROJECT_KEY
    
    def find_item(self, key):
        """Implement this to find items when they are not in the cache"""
        pass
    
    def __setitem__(self, key, value):
        cache_key = self.get_cache_key(key)
        self._set(cache_key, value)
    
    def __getitem__(self, key):
        cache_key = self.get_cache_key(key)
        
        # Attempt to get the value from cache
        value = cache.get(_hash(cache_key))
        
        # If the value was not found in the cache then try the database
        return value or self.find_item(key)