from django import template
from django.contrib.sites.models import Site

register = template.Library()

@register.simple_tag
def get_site_id():
    current_site = Site.objects.get_current()
    return current_site.id

@register.simple_tag
def get_foundation_site():
    try:
        current_site = Site.objects.get(id=2)
    except:
        current_site = '/'

    return current_site
