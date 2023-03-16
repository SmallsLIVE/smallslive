#from oscar.apps.shipping import config
from oscar.apps.shipping import apps


class ShippingConfig(apps.ShippingConfig):
    name = 'oscar_apps.shipping'
