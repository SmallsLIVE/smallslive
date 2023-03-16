#from oscar.apps.basket import config
from oscar.apps.basket import apps


class BasketConfig(apps.BasketConfig):
    name = 'oscar_apps.basket'
