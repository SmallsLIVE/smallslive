#from oscar.apps.order import config
from oscar.apps.order import apps

class OrderConfig(apps.OrderConfig):
    label = 'order'
    name = 'oscar_apps.order'
    verbose_name = 'Order'
