#from oscar.apps.checkout import config
from oscar.apps.checkout import apps

class CheckoutConfig(apps.CheckoutConfig):
    name = 'oscar_apps.checkout'
