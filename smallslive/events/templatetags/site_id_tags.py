from django import template
from django.contrib.sites.models import Site

register = template.Library()

@register.simple_tag
def get_site_id():
    current_site = Site.objects.get_current()
    return current_site.id
