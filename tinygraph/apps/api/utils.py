from piston.handler import BaseHandler
from django.db.models.fields.related import ForeignKey

class ImprovedHandler(BaseHandler):
    """
    handles request that have had csrfmiddlewaretoken inserted 
    automatically by django's CsrfViewMiddleware
    
    and replaces foreign key fields with a reference to the actual object.
    """
    
    def flatten_dict(self, dct):
        result = super(ImprovedHandler, self).flatten_dict(dct)
        if 'csrfmiddlewaretoken' in result:
            del result['csrfmiddlewaretoken']
        return result
    
    def _resolve_fk(self, klass, key):
        if key in self.dct:
            try:
                self.dct[key] = klass.objects.get(pk=self.dct[key])
            except klass.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write('%s with primary key "%d" not found.' % (klass.__name__, self.dct[key]))
                self.error = resp
    
    def _handle_m2m(self, model, field_name):
        m2m_attr = getattr(self.instance, field_name)
        remove_key = field_name + '__remove'
        add_key = field_name + '__add'
        
        if remove_key in self.dct:
            pk_set = [int(pk) for pk in self.dct[remove_key].split(',')]
            for pk in pk_set:
                try:
                    m2m_attr.remove(model.objects.get(pk=pk))
                except model.DoesNotExist:
                    continue
            del self.dct[remove_key]
        elif add_key in self.dct:
            pk_set = [int(pk) for pk in self.dct[add_key].split(',')]
            for pk in pk_set:
                try:
                    m2m_attr.add(model.objects.get(pk=pk))
                except model.DoesNotExist:
                    continue
            del self.dct[add_key]

    def _resolve_extras(self, request):
        if request.data:
            self.dct = request.data.copy()
            self.error = None

            for field in self.model._meta.fields:
                if isinstance(field, ForeignKey):
                    self._resolve_fk(field.related.parent_model, field.name)
        
            if self.instance is not None:
                for field, model in self.model._meta.get_m2m_with_model():
                    self._handle_m2m(field.related.parent_model, field.name)

            request.data = self.dct
            return self.error or None

    def create(self, request):
        return self._resolve_extras(request) or super(ImprovedHandler, self).create(request)

    def update(self, request, *args, **kwargs):
        pkfield = self.model._meta.pk.name
        try:
            self.instance = self.queryset(request).get(pk=kwargs.get(pkfield))
        except self.model.DoesNotExist:
            pass
        return self._resolve_extras(request) or super(ImprovedHandler, self).update(request, *args, **kwargs)