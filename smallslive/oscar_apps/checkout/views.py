import logging
from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.utils import six
from django.utils.translation import ugettext as _
from django.views.generic import RedirectView, View
from oscar.apps.checkout import views as checkout_views
from oscar.apps.checkout import signals
from oscar.apps.checkout.views import OrderPlacementMixin
from oscar.apps.order.exceptions import UnableToPlaceOrder
from oscar.apps.payment.exceptions import RedirectRequired, UnableToTakePayment, PaymentError
from oscar.apps.payment.models import SourceType, Source
from oscar.core.loading import get_class
from oscar_stripe.facade import Facade
from oscar_apps.order.models import Order
from oscar_apps.payment.exceptions import RedirectRequiredAjax
from subscriptions.mixins import PayPalMixin
from .forms import PaymentForm, BillingAddressForm

OrderTotalCalculator = get_class(
    'checkout.calculators', 'OrderTotalCalculator')
Repository = get_class('shipping.repository', 'Repository')
Selector = get_class('partner.strategy', 'Selector')
selector = Selector()


logger = logging.getLogger('oscar.checkout')








class ShippingAddressView(checkout_views.ShippingAddressView):

    def get_template_names(self):
        if self.request.is_ajax():
            template_name = 'checkout/shipping_address_ajax.html'
        else:
            template_name = 'checkout/shipping_address.html'
        return [template_name]

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


class PaymentDetailsView(checkout_views.PaymentDetailsView, PayPalMixin):
    """
    In the case of AJAX  (new become a supporter flow - gifts), we need to
    split billing from payment to match the existing payment design.
    I couldn't find a way
    """

    def get_template_names(self):

        if not self.preview:
            if self.request.is_ajax():
                template_name = 'checkout/payment_details_ajax.html'
            else:
                template_name = 'checkout/payment_details.html'
        else:
            if self.request.is_ajax():
                template_name = 'checkout/preview_ajax.html'
            else:
                template_name = 'checkout/preview.html'

        return [template_name]

    def get_context_data(self, **kwargs):

        if 'form' not in kwargs:
            kwargs['form'] = PaymentForm(self.request.user)
        if 'billing_address_form' not in kwargs and self.request.user.is_authenticated():
            shipping_address = self.get_shipping_address(self.request.basket)
            if self.request.user.is_authenticated():
                billing_initial = self.get_billing_initial()
            else:
                billing_initial = {}

            kwargs['billing_address_form'] = BillingAddressForm(shipping_address, self.request.user,
                                                                initial=billing_initial)
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

        # We use a custom parameter to indicate if this is an attempt to place
        # an order (normally from the preview page).  Without this, we assume a
        # payment form is being submitted from the payment details view. In
        # this case, the form needs validating and the order preview shown.
        print(request.POST)
        if request.POST.get('action', '') == 'place_order':
            self.token = self.request.POST.get('card_token')
            return self.handle_place_order_submission(request)
        print('4')
        return self.handle_payment_details_submission(request)

    def handle_payment_details_submission(self, request):
        form = PaymentForm(self.request.user, request.POST)
        shipping_address = self.get_shipping_address(self.request.basket)
        payment_method = request.POST.get('payment_method')
        print(payment_method)
        print(form)
        user = self.request.user
        if user.is_authenticated():
            billing_address_form = BillingAddressForm(shipping_address, user, request.POST)
            if billing_address_form.is_valid():
                print billing_address_form.errors
                if billing_address_form.cleaned_data.get('billing_option') == "same-address":
                    self.checkout_session.bill_to_shipping_address()
                else:
                    if user:
                        address = billing_address_form.save()
                        self.checkout_session.bill_to_user_address(address)
            else:
                print('3')
                return self.render_payment_details(request, form=form,
                                                   billing_address_form=billing_address_form)
        else:
            billing_address_form = None

        if payment_method == 'paypal':
            print('4')
            return self.render_preview(request, billing_address_form=billing_address_form,
                                       payment_method='paypal')
        else:
            if form.is_valid():
                self.token = form.token
                self.checkout_session._set('payment', 'card_info', {
                    'name': form.cleaned_data['name'],
                    'last_4': form.cleaned_data['number'][-4:],
                })
                print('5')
                print(request)
                return self.render_preview(request, card_token=form.token, form=form,
                                           payment_method=payment_method,
                                           billing_address_form=billing_address_form)
            else:
                print(form.errors)
                return self.render_payment_details(request, form=form,
                                                   billing_address_form=billing_address_form)

    def handle_place_order_submission(self, request):
        print '****************************'
        print 'handle_place_order_submission'
        print 'Basket: ', request.basket
        print request.basket.pk
        print '****************************'

        payment_method = request.POST.get('payment_method')
        submission = self.build_submission()
        submission['payment_kwargs']['payment_method'] = payment_method
        print 'Submission: '
        print submission
        return self.submit(**submission)

    def submit(self, user, basket,
               shipping_address, shipping_method,  # noqa (too complex (10))
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

        print '*******************************'
        print 'Submit: '
        print order_total
        print payment_kwargs

        if payment_kwargs is None:
            payment_kwargs = {}
        if order_kwargs is None:
            order_kwargs = {}

        if not user.is_anonymous():
            first_name, last_name = user.first_name, user.last_name
            print first_name, last_name
        else:
            first_name, last_name = self.checkout_session.get_reservation_name()
            print first_name, last_name
        if first_name and last_name:
            order_kwargs.update({
                'first_name': first_name,
                'last_name': last_name
            })

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
            print 'try handle payment: '
            print order_number
            print  order_total
            self.handle_payment(order_number, order_total, basket_lines, **payment_kwargs)
        except RedirectRequired as e:
            # Redirect required (eg PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            return http.HttpResponseRedirect(e.url)
        except RedirectRequiredAjax as e:
            # Redirect required (eg PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            print '****************************'
            print 'JsonResponse: Basket: ', self.request.basket, ' ', self.request.basket.pk
            print 'Basket: ', basket, ' ', basket.pk
            print 'Submitted basket: ', self.checkout_session.get_submitted_basket_id()
            return http.JsonResponse({'payment_url': e.url})
        except UnableToTakePayment as e:
            # Something went wrong with payment but in an anticipated way.  Eg
            # their bankcard has expired, wrong card number - that kind of
            # thing. This type of exception is supposed to set a friendly error
            # message that makes sense to the customer.
            msg = six.text_type(e) + "."
            error_msg = error_msg.format(msg)
            print '******************'
            print 'UnableToTakePayment: '
            print error_msg
            logger.warning(
                "Order #%s: unable to take payment (%s) - restoring basket",
                order_number, msg)
            self.restore_frozen_basket()

            # We assume that the details submitted on the payment details view
            # were invalid (eg expired bankcard).
            if self.request.is_ajax():
                return http.JsonResponse({'error': error_msg})
            else:
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
            print '******************'
            print 'PaymentError: '
            print error_msg

            if self.request.is_ajax():
                return http.JsonResponse({'error': error_msg})
            else:
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
            print '******************'
            print 'Unhandled Exception: '
            print error_msg

            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)

        print 'Send post payment signal'
        signals.post_payment.send_robust(sender=self, view=self)

        # If all is ok with payment, try and place order
        logger.info("Order #%s: payment successful, placing order",
                    order_number)
        try:
            print user
            print 'Handle order placement'
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

    def handle_successful_order(self, order):
        """
        Handle the various steps required after an order has been successfully
        placed.

        Overridden from OrderPlacementMixin.
        """
        # Send confirmation message (normally an email)
        order_type_code = 'ORDER_PLACED'
        first_element_type = order.lines.first().product.get_product_class().name
        if first_element_type == 'Tickets':
            order_type_code = 'TICKET_PLACED'
        self.send_confirmation_message(order, order_type_code)

        # Flush all session data
        self.checkout_session.flush()

        # Save order id in session so thank-you page can load it
        self.request.session['checkout_order_id'] = order.id
        if self.request.is_ajax():
            response = http.JsonResponse({'success_url': reverse('become_supporter_complete')})
        else:
            response = http.HttpResponseRedirect(self.get_success_url())
            self.send_signal(self.request, response, order)

        return response

    def get_item_list(self, basket_lines):

        items = []
        for line in basket_lines:
            item = {
                'name': line.product.get_title(),
                'price': str(line.unit_price_excl_tax),
                "sku": "N/A",
                'currency': 'USD',
                'quantity': line.quantity}
            items.append(item)

        print '***********************'
        print 'Items: '
        print items

        return items

    def handle_payment(self, order_number, total, basket_lines, **kwargs):

        card_token = self.request.POST.get('card_token')
        payment_method = kwargs.get('payment_method')

        print '*******************'
        print 'handle_payment: '
        print 'Card token: ', card_token
        print 'Payment method: ', payment_method
        print total

        if card_token:
            if card_token.startswith('card_'):
                stripe_ref = Facade().charge(
                    order_number,
                    total,
                    card=card_token,
                    description=self.payment_description(order_number, total, **kwargs),
                    metadata=self.payment_metadata(order_number, total, basket_lines, **kwargs),
                    customer=self.request.user.customer.stripe_id)
            else:
                stripe_ref = Facade().charge(
                    order_number,
                    total,
                    card=card_token,
                    description=self.payment_description(order_number, total, **kwargs),
                    metadata=self.payment_metadata(order_number, total, basket_lines, **kwargs))

            source_name = 'Credit Card'
            reference = stripe_ref
            currency = settings.STRIPE_CURRENCY
        elif payment_method == 'paypal':
            item_list = self.get_item_list(basket_lines)
            payment_execute_url = self.request.build_absolute_uri(reverse('checkout:paypal_execute'))
            payment_cancel_url = self.request.build_absolute_uri(reverse('become_supporter'))
            currency = total.currency
            total = str(total.incl_tax)
            # Donation will be set to True  if user is selecting gifts
            # For Tickets and  other goods, there will  be no donation.
            self.handle_paypal_payment(currency, total, item_list,
                                       payment_execute_url, payment_cancel_url,
                                       donation=True)
            source_name = 'PayPal'
            reference = ''
            currency = 'USD'

        source_type, __ = SourceType.objects.get_or_create(name=source_name)
        source = Source(
            source_type=source_type,
            currency=currency,
            amount_allocated=total.incl_tax,
            amount_debited=total.incl_tax,
            reference=reference)
        self.add_payment_source(source)

        self.add_payment_event('Purchase', total.incl_tax)

    def payment_description(self, order_number, total, **kwargs):
        return 'Order #{0} at SmallsLIVE'.format(order_number)

    def payment_metadata(self, order_number, total, basket_lines, **kwargs):
        items = {}
        for idx, item in enumerate(basket_lines, start=1):
            item_key = u'item{0}'.format(idx)
            items[item_key] = u'{0}, qty: {1}'.format(item.product.get_title(), item.quantity)
        items['order_number'] = order_number
        return items


class ExecutePayPalPaymentView(OrderPlacementMixin, PayPalMixin, View):
    """
    """

    def get(self, request, *args, **kwargs):

        """
        Receive callback from PayPal after the user has authorized the payment there.
        GET /store/checkout/paypal/execute/?paymentId=PAY-1LV98277E5422594XLP4E2MY&token=EC-1FB41424NL964725H&PayerID=EXH9W7JL6NSN8
        Confirm the payment and place the order
        """

        try:
            payment_id = self.execute_payment()

        except UnableToTakePayment as e:
            # Something went wrong with payment but in an anticipated way.  Eg
            # their bankcard has expired, wrong card number - that kind of
            # thing. This type of exception is supposed to set a friendly error
            # message that makes sense to the customer.
            error_msg = "{0} No payment has been taken. Please " \
                        "<a href='mailto:smallslive@gmail.com' tabindex='-1'>contact customer service</a> if this problem persists"
            msg = six.text_type(e) + "."
            error_msg = error_msg.format(msg)
            self.restore_frozen_basket()

            return self.render_payment_details(
                self.request, error=error_msg)

        # request.basket doesn't work b/c the basket is frozen
        basket = self.get_submitted_basket()
        strategy = selector.strategy(request=request, user=request.user)
        basket.strategy = strategy
        self.handle_order_placement(basket, payment_id)

        return http.HttpResponseRedirect(reverse(
            'become_supporter_complete') + '?payment_id={}'.format(payment_id))

    def handle_order_placement(self, basket, payment_id):
        order_number = self.checkout_session.get_order_number()

        total_incl_tax = basket.total_incl_tax
        # Record payment source
        source_type, is_created = SourceType.objects.get_or_create(name='PayPal')
        source = Source(source_type=source_type,
                        currency='USD',
                        amount_allocated=total_incl_tax,
                        amount_debited=total_incl_tax,
                        reference=payment_id)
        self.add_payment_source(source)

        shipping_address = self.get_shipping_address(self.request.basket)
        shipping_method = Repository().get_default_shipping_method(
            basket=self.request.basket, user=self.request.user,
            request=self.request)
        shipping_charge = shipping_method.calculate(self.request.basket)
        order_total = self.get_order_totals(
            basket, shipping_charge=shipping_charge)
        billing_address = self.get_billing_address(shipping_address)
        # Place order
        super(ExecutePayPalPaymentView, self).handle_order_placement(
            order_number, self.request.user, basket,
            shipping_address, shipping_method, shipping_charge,
            billing_address, order_total)
