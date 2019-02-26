from django import template
from oscar_apps.partner.strategy import Selector

register = template.Library()


@register.assignment_tag
def purchase_info_for_track(request, product):

    return Selector().track_strategy().fetch_for_product(product)

