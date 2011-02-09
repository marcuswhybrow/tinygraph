from django.template.defaultfilters import stringfilter
from django import template

from core.utils import datetime_to_timestamp

register = template.Library()

@register.filter
def timestamp(value):
    return datetime_to_timestamp(value) * 1000