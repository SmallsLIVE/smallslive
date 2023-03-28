#from oscar.apps.shipping import config
from oscar.apps.shipping import apps


class ShippingConfig(apps.ShippingConfig):
    label = 'shipping'
    name = 'oscar_apps.shipping'
    verbose_name = 'Shipping'
