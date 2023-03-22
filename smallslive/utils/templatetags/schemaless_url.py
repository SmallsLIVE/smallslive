from django import template

register = template.Library()


@register.filter
def schemaless_url(value):
    value = value.replace('http://', '').replace('https://', '')
    if value[-1] == '/':
        value = value[:-1]
    return value
