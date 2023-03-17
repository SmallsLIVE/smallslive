#from oscar.apps.checkout import config
from oscar.apps.customer import apps


class CustomerConfig(apps.CustomerConfig):
    name = 'oscar_apps.customer'
