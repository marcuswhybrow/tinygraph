from tinygraph.apps.core.cacher import BaseCacher, PROJECT_KEY
from tinygraph.apps.definitions.models import DataObject

DATA_OBJECT_KEY = 'data_objects'

class DefinitionsCacher(BaseCacher):
    def get_cache_key(self, key):
        identifier = key
        project_Key = super(DefinitionsCacher, self).get_cache_key(key)
        return '%s:%s:%s' % (project_Key, DATA_OBJECT_KEY, identifier)
    
    def find_item(self, key):
        identifier = key
        try:
            data_object = DataObject.objects.get(identifier=identifier)
        except DataObject.DoesNotExist:
            return
        else:
            value = data_object.derived_name
            self._set(self.get_cache_key(key), value)
            return value

cacher = DefinitionsCacher()