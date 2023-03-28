#from oscar.apps.checkout import config
from oscar.apps.checkout import apps

class CheckoutConfig(apps.CheckoutConfig):
    label = 'checkout'
    name = 'oscar_apps.checkout'
    verbose_name = 'Checkout'
