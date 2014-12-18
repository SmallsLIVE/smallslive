from decimal import Decimal as D

from oscar.apps.shipping import repository, methods, models


class Standard(methods.FixedPrice):
    code = "standard"
    name = "Standard"
    charge_excl_tax = D('10.00')


class Express(methods.FixedPrice):
    code = "express"
    name = "Express"
    charge_excl_tax = D('20.00')


class InternationalStandard(methods.FixedPrice):
    code = "int_standard"
    name = "International Standard"
    charge_excl_tax = D('10.00')


class Repository(repository.Repository):

    def get_available_shipping_methods(
            self, basket, shipping_addr=None, **kwargs):
        methods = [Standard(), Express()]
        if shipping_addr and shipping_addr.country.code != 'US':
            methods = [InternationalStandard()]
        # if shipping_addr:
        #     item_methods = models.OrderAndItemCharges.objects.filter(
        #         countries=shipping_addr.country)
        #     methods.extend(list(item_methods))

        return methods
