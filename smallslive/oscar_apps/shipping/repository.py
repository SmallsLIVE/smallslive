from decimal import Decimal as D

from oscar.apps.shipping import repository, methods, models


class Standard(methods.FixedPrice):
    code = "standard"
    name = "Standard"
    charge_excl_tax = D('10.00')
    charge_incl_tax = D('10.00')


class Repository(repository.Repository):

    def get_available_shipping_methods(
            self, basket, shipping_addr=None, **kwargs):
        return [Standard()]
