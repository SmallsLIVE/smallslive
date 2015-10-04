from django import http
from django.conf import settings
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from oscar.apps.checkout import views as checkout_views
from oscar.apps.payment.models import SourceType, Source
from oscar.core.loading import get_class
from oscar_stripe.facade import Facade
from .forms import PaymentForm, BillingAddressForm

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
    
    def get_initial(self):
        initial = super(ShippingAddressView, self).get_initial()
        if not initial:
            address = self.get_available_addresses().first()
            if address:
                initial = model_to_dict(address)
        return initial


class PaymentDetailsView(checkout_views.PaymentDetailsView):
    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = PaymentForm(self.request.user)
        if 'billing_address_form' not in kwargs:
            shipping_address = self.get_shipping_address(self.request.basket)
            kwargs['billing_address_form'] = BillingAddressForm(shipping_address, self.request.user,
                                                                initial=self.get_billing_initial())
        if hasattr(self, 'token'):
            kwargs['stripe_token'] = self.token
        return super(PaymentDetailsView, self).get_context_data(**kwargs)

    def get_billing_initial(self):
        address = self.get_default_billing_address()
        if address:
            initial = model_to_dict(address)
            return initial
        else:
            return None

    def post(self, request, *args, **kwargs):
        # Posting to payment-details isn't the right thing to do.  Form
        # submissions should use the preview URL.
        if not self.preview:
            return http.HttpResponseBadRequest()

        if request.POST.get('payment_method') == 'paypal':
            return redirect('paypal-direct-payment')

        # We use a custom parameter to indicate if this is an attempt to place
        # an order (normally from the preview page).  Without this, we assume a
        # payment form is being submitted from the payment details view. In
        # this case, the form needs validating and the order preview shown.
        if request.POST.get('action', '') == 'place_order':
            self.token = self.request.POST.get('card_token')
            return self.handle_place_order_submission(request)
        return self.handle_payment_details_submission(request)

    def handle_payment_details_submission(self, request):
        form = PaymentForm(self.request.user, request.POST)
        shipping_address = self.get_shipping_address(self.request.basket)
        billing_address_form = BillingAddressForm(shipping_address, self.request.user, request.POST)
        if form.is_valid() and billing_address_form.is_valid():
            if billing_address_form.cleaned_data.get('billing_option') == "same-address":
                self.checkout_session.bill_to_shipping_address()
            else:
                address = billing_address_form.save()
                self.checkout_session.bill_to_user_address(address)
                self.token = form.token
            return self.render_preview(request, card_token=form.token, form=form,
                                       billing_address_form=billing_address_form)
        else:
            return self.render_payment_details(request, form=form, billing_address_form=billing_address_form)

    def handle_payment(self, order_number, total, **kwargs):
        card_token = self.request.POST.get('card_token')
        if card_token.startswith('card_'):
            stripe_ref = Facade().charge(
                order_number,
                total,
                card=card_token,
                description=self.payment_description(order_number, total, **kwargs),
                metadata=self.payment_metadata(order_number, total, **kwargs),
                customer=self.request.user.customer.stripe_id)
        else:
            stripe_ref = Facade().charge(
                order_number,
                total,
                card=card_token,
                description=self.payment_description(order_number, total, **kwargs),
                metadata=self.payment_metadata(order_number, total, **kwargs))

        source_type, __ = SourceType.objects.get_or_create(name='Credit Card')
        source = Source(
            source_type=source_type,
            currency=settings.STRIPE_CURRENCY,
            amount_allocated=total.incl_tax,
            amount_debited=total.incl_tax,
            reference=stripe_ref)
        self.add_payment_source(source)

        self.add_payment_event('Purchase', total.incl_tax)

    def payment_description(self, order_number, total, **kwargs):
        return "Order #{0} at SmallsLIVE".format(order_number)

    def payment_metadata(self, order_number, total, **kwargs):
        return {'order_number': order_number}
