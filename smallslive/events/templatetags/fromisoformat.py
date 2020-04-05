import dateutil.parser

from django.template import Library

register = Library()


@register.filter(is_safe=True)
def fromisoformat(obj):
    return dateutil.parser.parse(obj)
