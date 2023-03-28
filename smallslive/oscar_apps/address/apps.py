#from oscar.apps.address import config
from oscar.apps.address import apps


class AddressConfig(apps.AddressConfig):
    label = 'address'
    name = 'oscar_apps.address'
    verbose_name = 'Address'
