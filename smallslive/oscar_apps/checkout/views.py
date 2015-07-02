from django import http
from django.shortcuts import redirect
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


class PaymentDetailsView(checkout_views.PaymentDetailsView):
    def post(self, request, *args, **kwargs):
        # Posting to payment-details isn't the right thing to do.  Form
        # submissions should use the preview URL.
        if not self.preview:
            return http.HttpResponseBadRequest()

        if request.POST.get('payment-method') == 'paypal':
            return redirect('paypal-direct-payment')

        # We use a custom parameter to indicate if this is an attempt to place
        # an order (normally from the preview page).  Without this, we assume a
        # payment form is being submitted from the payment details view. In
        # this case, the form needs validating and the order preview shown.
        if request.POST.get('action', '') == 'place_order':
            return self.handle_place_order_submission(request)
        return self.handle_payment_details_submission(request)
