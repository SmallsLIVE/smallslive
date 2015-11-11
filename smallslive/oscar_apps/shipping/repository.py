from decimal import Decimal as D

from oscar.apps.shipping import repository, methods, models


class Domestic(methods.Free):
    code = "domestic"
    name = "Domestic"


class International(methods.FixedPrice):
    ode = "international"
    name = "International"
    charge_excl_tax = D('10.00')
    charge_incl_tax = D('10.00')


class Repository(repository.Repository):

    def get_available_shipping_methods(
            self, basket, shipping_addr=None, **kwargs):
        if shipping_addr:
            if shipping_addr.country.code == 'US':
                methods = (Domestic(),)
            else:
                methods = (International(),)
        else:
            methods = self.methods
        return methods
