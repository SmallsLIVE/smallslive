import logging
from django import http
from django.conf import settings
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.utils import six
from django.utils.translation import ugettext as _
from oscar.apps.checkout import views as checkout_views
from oscar.apps.checkout import signals
from oscar.apps.order.exceptions import UnableToPlaceOrder
from oscar.apps.payment.exceptions import RedirectRequired, UnableToTakePayment, PaymentError
from oscar.apps.payment.models import SourceType, Source
from oscar.core.loading import get_class
from oscar_stripe.facade import Facade
from .forms import PaymentForm, BillingAddressForm
from oscar_apps.order.models import Order

OrderTotalCalculator = get_class(
    'checkout.calculators', 'OrderTotalCalculator')
Repository = get_class('shipping.repository', ('Repository'))

logger = logging.getLogger('oscar.checkout')


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

        kwargs['card_info'] = self.checkout_session._get('payment', 'card_info')
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
            self.checkout_session._set('payment', 'card_info', {
                'name': form.cleaned_data['name'],
                'last_4': form.cleaned_data['number'][-4:],
            })
            return self.render_preview(request, card_token=form.token, form=form,
                                       billing_address_form=billing_address_form)
        else:
            return self.render_payment_details(request, form=form, billing_address_form=billing_address_form)

    def submit(self, user, basket, shipping_address, shipping_method,  # noqa (too complex (10))
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None):
        """
        Submit a basket for order placement.

        The process runs as follows:

         * Generate an order number
         * Freeze the basket so it cannot be modified any more (important when
           redirecting the user to another site for payment as it prevents the
           basket being manipulated during the payment process).
         * Attempt to take payment for the order
           - If payment is successful, place the order
           - If a redirect is required (eg PayPal, 3DSecure), redirect
           - If payment is unsuccessful, show an appropriate error message

        :basket: The basket to submit.
        :payment_kwargs: Additional kwargs to pass to the handle_payment
                         method. It normally makes sense to pass form
                         instances (rather than model instances) so that the
                         forms can be re-rendered correctly if payment fails.
        :order_kwargs: Additional kwargs to pass to the place_order method
        """
        if payment_kwargs is None:
            payment_kwargs = {}
        if order_kwargs is None:
            order_kwargs = {}

        # Taxes must be known at this point
        assert basket.is_tax_known, (
            "Basket tax must be set before a user can place an order")
        assert shipping_charge.is_tax_known, (
            "Shipping charge tax must be set before a user can place an order")

        # We generate the order number first as this will be used
        # in payment requests (ie before the order model has been
        # created).  We also save it in the session for multi-stage
        # checkouts (eg where we redirect to a 3rd party site and place
        # the order on a different request).
        order_number = self.generate_order_number(basket)
        self.checkout_session.set_order_number(order_number)
        logger.info("Order #%s: beginning submission process for basket #%d",
                    order_number, basket.id)

        # Freeze the basket so it cannot be manipulated while the customer is
        # completing payment on a 3rd party site.  Also, store a reference to
        # the basket in the session so that we know which basket to thaw if we
        # get an unsuccessful payment response when redirecting to a 3rd party
        # site.
        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        # We define a general error message for when an unanticipated payment
        # error occurs.
        error_msg = "{0} No payment has been taken. Please " \
                    "<a href='mailto:smallslive@gmail.com' tabindex='-1'>contact customer service</a> if this problem persists"

        signals.pre_payment.send_robust(sender=self, view=self)
        basket_lines = basket.lines.all()
        try:
            self.handle_payment(order_number, order_total, basket_lines, **payment_kwargs)
        except RedirectRequired as e:
            # Redirect required (eg PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            return http.HttpResponseRedirect(e.url)
        except UnableToTakePayment as e:
            # Something went wrong with payment but in an anticipated way.  Eg
            # their bankcard has expired, wrong card number - that kind of
            # thing. This type of exception is supposed to set a friendly error
            # message that makes sense to the customer.
            msg = six.text_type(e) + "."
            error_msg = error_msg.format(msg)
            logger.warning(
                "Order #%s: unable to take payment (%s) - restoring basket",
                order_number, msg)
            self.restore_frozen_basket()

            # We assume that the details submitted on the payment details view
            # were invalid (eg expired bankcard).
            return self.render_payment_details(
                self.request, error=error_msg, **payment_kwargs)
        except PaymentError as e:
            # A general payment error - Something went wrong which wasn't
            # anticipated.  Eg, the payment gateway is down (it happens), your
            # credentials are wrong - that king of thing.
            # It makes sense to configure the checkout logger to
            # mail admins on an error as this issue warrants some further
            # investigation.
            msg = six.text_type(e) + "."
            logger.error("Order #%s: payment error (%s)", order_number, msg,
                         exc_info=True)
            self.restore_frozen_basket()
            error_msg = error_msg.format(msg)
            return self.render_payment_details(
                self.request, error=error_msg, **payment_kwargs)
        except Exception as e:
            # Unhandled exception - hopefully, you will only ever see this in
            # development...
            logger.error(
                "Order #%s: unhandled exception while taking payment (%s)",
                order_number, e, exc_info=True)
            self.restore_frozen_basket()
            error_msg = error_msg.format("")
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)

        signals.post_payment.send_robust(sender=self, view=self)

        # If all is ok with payment, try and place order
        logger.info("Order #%s: payment successful, placing order",
                    order_number)
        try:
            return self.handle_order_placement(
                order_number, user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, **order_kwargs)
        except UnableToPlaceOrder as e:
            # It's possible that something will go wrong while trying to
            # actually place an order.  Not a good situation to be in as a
            # payment transaction may already have taken place, but needs
            # to be handled gracefully.
            msg = six.text_type(e)
            logger.error("Order #%s: unable to place order - %s",
                         order_number, msg, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=msg, **payment_kwargs)

    def handle_payment(self, order_number, total, basket_lines, **kwargs):
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
                metadata=self.payment_metadata(order_number, total, basket_lines, **kwargs))

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

    def payment_metadata(self, order_number, total, basket_lines, **kwargs):
        items = {}
        for idx, item in enumerate(basket_lines, start=1):
            item_key = u"item{0}".format(idx)
            items[item_key] = u"{0}, qty: {1}".format(item.product.get_title(), item.quantity)
        items['order_number'] = order_number
        return items
