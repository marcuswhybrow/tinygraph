from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter
@stringfilter
def splitlast(value, arg):
    return value.split(arg)[-1]

@register.filter
@stringfilter
def subtract(value, arg):
    return value[len(arg)+1:]