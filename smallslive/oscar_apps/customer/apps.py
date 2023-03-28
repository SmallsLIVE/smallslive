#from oscar.apps.checkout import config
from oscar.apps.customer import apps


class CustomerConfig(apps.CustomerConfig):
    label = 'customer'
    name = 'oscar_apps.customer'
    verbose_name = 'Customer'
