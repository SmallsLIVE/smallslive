from oscar.apps.checkout import views as checkout_views
from oscar.core.loading import get_class

OrderTotalCalculator = get_class(
    'checkout.calculators', 'OrderTotalCalculator')
Repository = get_class('shipping.repository', ('Repository'))


class ShippingAddressView(checkout_views.ShippingAddressView):
    def get_context_data(self, **kwargs):
        context = super(ShippingAddressView, self).get_context_data(**kwargs)
        method = self.get_default_shipping_method(self.request.basket)
        shipping_charge = method.calculate(self.request.basket)
        context['shipping_charge'] = shipping_charge
        context['order_total'] = OrderTotalCalculator().calculate(
            self.request.basket, shipping_charge)
        return context

    def get_default_shipping_method(self, basket):
        return Repository().get_default_shipping_method(
            basket=self.request.basket, user=self.request.user,
            request=self.request)
