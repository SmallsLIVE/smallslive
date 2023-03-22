from django import template
from oscar_apps.partner.strategy import Selector

register = template.Library()


@register.simple_tag
def purchase_info_for_track(request, product):

    stock_record = product.get_track_stockrecord
    strategy = Selector().track_strategy().fetch_for_product(product, stock_record)
    return strategy

