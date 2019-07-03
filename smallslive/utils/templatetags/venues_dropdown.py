from django import template
from events.models import Venue

register = template.Library()


@register.inclusion_tag('venues_dropdown.html', takes_context=True)
def venues_dropdown(context):
    return {
        'venues': Venue.objects.all()
    }
