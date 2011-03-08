from piston.handler import BaseHandler

class CsrfBaseHandler(BaseHandler):
    """
    handles request that have had csrfmiddlewaretoken inserted 
    automatically by django's CsrfViewMiddleware
    """
    
    def flatten_dict(self, dct):
        result = super(CsrfBaseHandler, self).flatten_dict(dct)
        del result['csrfmiddlewaretoken']
        return result