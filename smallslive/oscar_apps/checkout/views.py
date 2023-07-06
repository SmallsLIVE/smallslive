from __future__ import absolute_import
import logging
from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.utils import six
from django.views.generic import View
from oscar.apps.address.models import Country
from oscar.apps.checkout import views as checkout_views, signals
from oscar.apps.checkout.exceptions import FailedPreCondition, PassedSkipCondition
from oscar.apps.checkout.mixins import OrderPlacementMixin
from oscar.apps.checkout.utils import CheckoutSessionData
from oscar.apps.order.exceptions import UnableToPlaceOrder
from oscar.apps.payment.exceptions import RedirectRequired, UnableToTakePayment, PaymentError
from oscar.apps.payment.models import SourceType, Source
from oscar.core.loading import get_class, get_model
from oscar_apps.catalogue.models import UserCatalogue, UserCatalogueProduct
from oscar_apps.payment.exceptions import RedirectRequiredAjax
from subscriptions.mixins import PayPalMixin, StripeMixin, PaymentCredentialsMixin
from subscriptions.models import Donation
from users.utils import send_admin_notification as util_send_admin_notification
from utils import utils as sl_utils
from .forms import PaymentForm, BillingAddressForm
from django.views import generic
from django.utils.translation import gettext as _


OrderTotalCalculator = get_class(
    'checkout.calculators', 'OrderTotalCalculator')
Repository = get_class('shipping.repository', 'Repository')
Selector = get_class('partner.strategy', 'Selector')
Order = get_model('order', 'Order')
selector = Selector()

logger = logging.getLogger('oscar.checkout')


class IndexView(checkout_views.IndexView):

    template_name = 'checkout/checkout-gateway.html'

    def get_success_response(self):
        url = self.get_success_url()
        if self.request.is_ajax():
            return http.JsonResponse({'url': url})
        else:
            return redirect(url)
        
    def get(self, request, *args, **kwargs):
        # We redirect immediately to shipping address stage if the user is
        # signed in.
        if request.user.is_authenticated:
            # We raise a signal to indicate that the user has entered the
            # checkout process so analytics tools can track this event.
            signals.start_checkout.send_robust(
                sender=self, request=request)
            return self.get_success_response()
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if form.is_guest_checkout():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            self.checkout_session.set_reservation_name(first_name, last_name)

        if form.is_guest_checkout() or form.is_new_account_checkout():
            email = form.cleaned_data['username']
            self.checkout_session.set_guest_email(email)

            # We raise a signal to indicate that the user has entered the
            # checkout process by specifying an email address.
            signals.start_checkout.send_robust(
                sender=self, request=self.request, email=email)

            if form.is_new_account_checkout():
                self.success_url = "%s?next=%s&email=%s" % (
                    reverse('customer:register'),
                    reverse('checkout:shipping-address'),
                    email
                )
        else:
            user = form.get_user()
            login(self.request, user)

            # We raise a signal to indicate that the user has entered the
            # checkout process.
            signals.start_checkout.send_robust(
                sender=self, request=self.request)

        return redirect(self.get_success_url())


class ShippingMethodView(checkout_views.ShippingMethodView):

    def get_success_response(self):
        url = reverse('checkout:payment-method')
        if self.request.is_ajax():
            return http.JsonResponse({'url': url})
        else:
            return redirect(url)


class ShippingAddressView(checkout_views.ShippingAddressView):

    def dispatch(self, request, *args, **kwargs):
        # Assign the checkout session manager so it's available in all checkout
        # views.
        self.checkout_session = CheckoutSessionData(request)

        # Enforce any pre-conditions for the view.
        try:
            self.check_pre_conditions(request)
        except FailedPreCondition as e:
            for message in e.messages:
                messages.warning(request, message)
            if request.is_ajax():
                return http.JsonResponse({'url': e.url})
            else:
                return http.HttpResponseRedirect(e.url)

        # Check if this view should be skipped
        try:
            self.check_skip_conditions(request)
        except PassedSkipCondition as e:
            if request.is_ajax():
                return http.JsonResponse({'url': e.url})
            else:
                return http.HttpResponseRedirect(e.url)

        return super(ShippingAddressView, self).dispatch(
            request, *args, **kwargs)

    def form_valid(self, form):
        address_fields = dict(
            (k, v) for (k, v) in form.instance.__dict__.items()
            if not k.startswith('_'))
        self.checkout_session.ship_to_new_address(address_fields)
        url = self.get_success_url()
        if self.request.is_ajax():
            return http.JsonResponse({'url': url})
        else:
            return redirect(url)

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

        initial = self.checkout_session.new_shipping_address_fields()
        if initial:
            initial = initial.copy()
            # Convert the primary key stored in the session into a Country
            # instance
            try:
                initial['country'] = Country.objects.get(
                    iso_3166_1_a2=initial.pop('country_id'))
            except Country.DoesNotExist:
                # Hmm, the previously selected Country no longer exists. We
                # ignore this.
                pass
        if not initial:
            address = self.get_available_addresses().first()
            if address:
                initial = model_to_dict(address)

        return initial


class PaymentMethodView(checkout_views.PaymentMethodView):

    def get_success_response(self):
        url = reverse('checkout:payment-details')
        if self.request.is_ajax():
            return http.JsonResponse({'url': url})
        else:
            return redirect(url)


class AssignProductMixin(object):

    def assign(self):
        # Assign products for Library
        for line in self.order.lines.all():
            category_list = []
            for category in line.product.get_categories().all():
                category_list.append(category.name)
            product_class = line.product.product_class
            if not product_class:
                product_class = line.product.parent.product_class
            if 'Full Access' in category_list or product_class.slug == 'full-access':
                if UserCatalogue.objects.filter(user=self.request.user).first():
                    UserCatalogue.objects.filter(user=self.request.user).update(has_full_catalogue_access=True)
                else:
                    UserCatalogue.objects.get_or_create(user=self.request.user, has_full_catalogue_access=True)
            if product_class.slug in ['physical-album', 'digital-album', 'track'] or line.product.misc_file:
                UserCatalogueProduct.objects.get_or_create(user=self.request.user, product=line.product)

            # Set status to completed for lines if it doesn't require shipping
            if not line.product.get_product_class().requires_shipping:
                line.set_status('Completed')

        if self.order.lines.count() == self.order.digital_lines().count():
            self.order.set_status('Completed')


class SuccessfulOrderMixin(PaymentCredentialsMixin):

    def set_payment_target(self):
        if 'product_id' in self.request.session:
            self.product_id = self.request.session['product_id']

        if 'event_id' in self.request.session:
            self.event_id = self.request.session['event_id']
            self.event_slug = self.request.session['event_slug']

        if 'artist_id' in self.request.session:
            self.artist_id = self.request.session['artist_id']

    def create_donation(self):
        is_foundation = self.get_payment_accounts()[0]
        if is_foundation:
            payment_source = 'PayPal Foundation'
            if self.card_token:
                payment_source = 'Stripe Foundation'
            Donation.objects.create_by_order(
                self.order,
                payment_source,
                artist_id=self.artist_id, event_id=self.event_id, product_id=self.product_id)

    def send_confirmation(self):
        order_type_code = 'ORDER_PLACED'
        if self.order.has_tickets():
            order_type_code = 'TICKET_PLACED'
        if self.order.basket.has_gifts():
            order_type_code = 'GIFT_PLACED'

        # Send confirmation message (normally an email)
        self.send_confirmation_message(self.order, order_type_code)
        self.send_admin_notification()

    def send_admin_notification(self):
        if self.order.has_physical_products():
            util_send_admin_notification(self.order.number)

    def get_success_url(self, flow_type):
        success_url = reverse('become_supporter_complete')
        user = self.request.user
        if not user.is_authenticated:
            success_url = reverse('checkout:thank-you')
        if flow_type:
            success_url += '?flow_type=' + flow_type
            # remove flow_type from session
            del self.request.session['flow_type']

            if 'product_id' in self.request.session:
                del self.request.session['product_id']

            if 'event_id' in self.request.session:
                del self.request.session['event_id']
                del self.request.session['event_slug']

            if 'artist_id' in self.request.session:
                del self.request.session['artist_id']

            sl_utils.clean_messages(self.request)

            if self.payment_id:
                success_url += '&payment_id=' + self.payment_id

            if self.event_id:
                success_url += '&event_id=' + self.event_id
                success_url += '&event_slug=' + self.event_slug

            if self.artist_id:
                success_url += '&artist_id=' + self.artist_id

        return success_url

    def handle(self):
        """
        Handle the various steps required after an order has been successfully
        placed.
        """

        # Donating or paying for a product, event, artist, etc.
        self.set_payment_target()

        self.create_donation()

        # Assign product to Library if applies and set order and line status.
        self.assign()

        #  Save order id in session so thank-you page can load
        self.request.session['checkout_order_id'] = self.order.id

        # Flush all session data
        self.checkout_session.flush()

        # Get flow type from session
        flow_type = self.request.session.get('flow_type')

        if flow_type == 'catalog_selection':
            response = http.JsonResponse({'success_url': self.get_success_url()})
        elif self.request.is_ajax():
            success_url = self.get_success_url(flow_type)
            response = http.JsonResponse({'success_url': success_url})
        else:
            response = http.HttpResponseRedirect(self.get_success_url(flow_type))

        if self.order:
            self.send_signal(self.request, response, self.order)
            self.send_confirmation()

        return response


class PaymentDetailsView(PayPalMixin, StripeMixin, AssignProductMixin,
                         SuccessfulOrderMixin, checkout_views.PaymentDetailsView):
    """
    Extended from Oscar.
    Takes payment, renders order preview and takes order submission.
    Some payment types can be processed online (Stripe) and others need
    redirection to the vendor's website (PayPal). Those will be completed by
    a different class (ExecutePayPalPaymentView).
    """

    def __init__(self, *args, **kwargs):
        """
        product_id: Product the payment goes to.
        artist_id: Artist the payment goes to.
        event_id: Event the payment goes to.
        card_token: Stripe token.
        amount: Item price.
        payment_id: Id provided by payment gateway.
        order: Oscar order instance.
        ticket_type: ticket type (mezzrow or smalls) if currently processing a ticket.
        ticket_name: information about purchase
        """
        super(PaymentDetailsView, self).__init__(*args, **kwargs)
        self.amount = None
        self.card_token = None
        self.artist_id = None
        self.event = None
        self.event_id = None
        self.event_slug = None
        self.product_id = None
        self.order = None
        self.payment_id = None
        self.tickets_type = None
        self.ticket_name = {}
        self.total = None
        self.total_deductable = None

    def get_template_names(self):
        """
        Different templates are rendered according to conditions.
        """

        if not self.preview:
            if self.request.is_ajax():
                template_name = 'checkout/payment_details_ajax.html'
            else:
                if self.request.basket.has_tickets():  # TODO: add venue__name='Mezzrow'
                    template_name = 'checkout/payment_details_tickets.html'
                else:
                    template_name = 'checkout/payment_details.html'
        else:
            if self.request.is_ajax():
                if self.request.basket.has_tickets():
                    template_name = 'checkout/preview_tickets_ajax.html'
                else:
                    template_name = 'checkout/preview_ajax.html'
            else:
                if self.request.basket.has_tickets():
                    template_name = 'checkout/preview_tickets.html'
                else:
                    template_name = 'checkout/preview.html'

        return [template_name]

    def get_context_data(self, **kwargs):

        reservation_name = self.checkout_session.get_reservation_name()
        if not self.request.user.is_authenticated:
            kwargs['guest'] = {
                'first_name': reservation_name[0],
                'last_name': reservation_name[1]
            }
        if reservation_name[0]:
            kwargs["reservation_string"] = '{} {}'.format(reservation_name[0], reservation_name[1])

        basket = self.request.basket

        if basket.has_tickets():
            kwargs.update(self.get_tickets_context(**kwargs))
        else:
            kwargs.update(self.get_basket_context(basket))

        return super(PaymentDetailsView, self).get_context_data(**kwargs)

    def get_tickets_context(self, **kwargs):
        reservation_name = self.checkout_session.get_reservation_name()
        if not self.request.user.is_authenticated:
            kwargs['guest'] = {
                'first_name': reservation_name[0],
                'last_name': reservation_name[1]
            }
        if reservation_name:
            kwargs['reservation_string'] = '{} {}'.format(reservation_name[0], reservation_name[1])

        kwargs['card_info'] = self.checkout_session._get('payment', 'card_info')

        return kwargs

    def get_basket_context(self, basket):
        kwargs = {}
        kwargs['form'] = kwargs.get('form', PaymentForm(self.request.user, settings.STRIPE_SECRET_KEY))
        if 'billing_address_form' not in kwargs and self.request.user.is_authenticated:
            shipping_address = self.get_shipping_address(basket)
            billing_initial = self.get_billing_initial()
            kwargs['billing_address_form'] = BillingAddressForm(
                shipping_address, self.request.user,
                initial=billing_initial)

        if hasattr(self, 'token'):
            kwargs['stripe_token'] = self.token

        kwargs['card_info'] = self.checkout_session._get('payment', 'card_info')
        user = self.request.user
        if user.is_authenticated:
            kwargs['can_use_existing_cc'] = user.can_use_existing_cc and not basket.has_catalog()

        return kwargs

    def get_billing_initial(self):
        address = self.get_default_billing_address()
        if not address:
            address = self.request.user.addresses.first()
        if address:
            initial = model_to_dict(address)
            return initial
        else:
            return None

    def post(self, request, *args, **kwargs):
        """
        Take order submission.
        """

        # Posting to payment-details isn't the right thing to do.  Form
        # submissions should use the preview URL.
        if not self.preview:
            return http.HttpResponseBadRequest()

        first_name = self.request.POST.get('guest_first_name', '')
        last_name = self.request.POST.get('guest_last_name', '')
        if first_name and last_name:
            self.checkout_session.set_reservation_name(first_name, last_name)

        # We use a custom parameter to indicate if this is an attempt to place
        # an order (normally from the preview page).  Without this, we assume a
        # payment form is being submitted from the payment details view. In
        # this case, the form needs validating and the order preview shown.
        if request.POST.get('action', '') == 'place_order':
            self.card_token = self.request.POST.get('card_token')
            return self.handle_place_order_submission(request)

        return self.handle_payment_details_submission(request)

    def handle_payment_details_submission(self, request):
        """
        Process payment. Stripe can be processed immediately, while
        PayPal will require a redirect and be finished in another class.
        """
        basket = request.basket
        shipping_address = self.get_shipping_address(basket)
        billing_address_form = None
        if not basket.has_tickets():
            billing_address_form = self.handle_billing_address(shipping_address, request.user)
        payment_method = request.POST.get('payment_method')
        if basket.has_tickets():
            return self.handle_payment_details_submission_for_tickets(
                billing_address_form, payment_method)
        else:
            return self.handle_payment_details_submission_for_basket(
                shipping_address, billing_address_form, payment_method)

    def handle_billing_address(self, shipping_address, user):
        if user.is_authenticated:
            billing_address_form = BillingAddressForm(shipping_address, user, self.request.POST)
            if billing_address_form.is_valid():
                if billing_address_form.cleaned_data.get('billing_option') == 'same-address':
                    self.checkout_session.bill_to_shipping_address()
                else:
                    if user:
                        address = billing_address_form.save()
                        self.checkout_session.bill_to_user_address(address)
            else:
                print('** billing address form invalid **')
                print(billing_address_form.errors)
                billing_address_form = None
        else:
            billing_address_form = None

        return billing_address_form


    def handle_payment_details_submission_for_tickets(self,
                                                      billing_address_form,
                                                      payment_method):
        """Customer can pay for Mezzrow or Smalls tickets with PayPal or Credit Card."""

        self.event = self.request.basket.get_tickets_event()
        stripe_api_key = self.get_stripe_payment_credentials()[2]

        form = PaymentForm(self.request.user, stripe_api_key, self.request.POST)

        if payment_method == 'paypal':
            return self.render_preview(self.request, billing_address_form=billing_address_form,
                                       payment_method='paypal')
        else:

            first_name, last_name = self.checkout_session.get_reservation_name()
            if first_name and last_name:
                reservation_string = '{} {}'.format(first_name, last_name)
            else:
                return http.JsonResponse({'success': False, 'message': "Please enter a name for your reservation under PARTY NAME above"})

            if payment_method == 'existing-credit-card':
                for field in form.fields:
                    if field != 'payment_method':
                        form.fields[field].required = False

            if form.is_valid():
                self.card_token = form.token
                self.checkout_session._set('payment', 'card_info', {
                    'name': form.cleaned_data['name'],
                    'last_4': form.cleaned_data['card_number'][-4:],
                })

                return self.render_preview(self.request, card_token=form.token, form=form,
                                           payment_method=payment_method,
                                           reservation_string=reservation_string)
            else:
                if self.request.is_ajax:
                    error_message = "<br>".join(["* {} * {}".format(field.replace('_', ' ').title(), errors[0]) for field, errors in form.errors.items()])
                    return http.JsonResponse({'success': False, 'message': error_message})
                else:
                    return self.render_payment_details(self.request, form=form,
                                                       payment_method=payment_method,
                                                       reservation_string=reservation_string)

    def handle_payment_details_submission_for_basket(
            self, shipping_address, billing_address_form, payment_method):

        stripe_api_key = self.get_stripe_payment_credentials()[2]
        form = PaymentForm(self.request.user, stripe_api_key, self.request.POST)

        if billing_address_form and not billing_address_form.is_valid():
            print('*** error ****')
            return self.render_payment_details(self.request, form=form,
                                               billing_address_form=billing_address_form)

        first_name, last_name = self.checkout_session.get_reservation_name()
        reservation_string = ''
        if first_name and last_name:
            reservation_string = '{} {}'.format(first_name, last_name)

        if payment_method == 'paypal':
            return self.render_preview(self.request, billing_address_form=billing_address_form,
                                       payment_method='paypal')
        else:
            if payment_method == 'existing-credit-card':
                for field in form.fields:
                    if field != 'payment_method':
                        form.fields[field].required = False
            if form.is_valid():
                self.card_token = form.token
                self.checkout_session._set('payment', 'card_info', {
                    'name': form.cleaned_data['name'],
                    'last_4': form.cleaned_data['card_number'][-4:],
                })
                return self.render_preview(self.request, card_token=form.token, form=form,
                                           payment_method=payment_method,
                                           billing_address_form=billing_address_form,
                                           reservation_string=reservation_string)
            else:
                if self.request.is_ajax:
                    error_message = "<br>".join(
                        ["* {} * {}".format(field.replace('_', ' ').title(), errors[0]) for field, errors in
                         form.errors.items()])
                    return http.JsonResponse({'success': False, 'message': error_message})
                else:
                    return self.render_payment_details(self.request, form=form,
                                                       billing_address_form=billing_address_form,
                                                       reservation_string=reservation_string)

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.

        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            **response_kwargs
        )

    def handle_place_order_submission(self, request):

        payment_method = request.POST.get('payment_method')

        self.product_id = request.POST.get('product_id') or None
        if self.product_id:
            request.session['product_id'] = self.product_id

        self.event_id = request.POST.get('event_id') or None
        self.event_slug = request.POST.get('event_slug') or None
        if self.event_id:
            # Use session to retrieve parameters after PayPal payment redirect.
            # Could be stored on Order but that would mean adding event_id to all orders.
            # PayPal has no mechanism to return parameters.
            request.session['event_id'] = self.event_id
            request.session['event_slug'] = self.event_slug

        self.artist_id = request.POST.get('artist_id') or None
        if self.artist_id:
            # Use session to retrieve parameters after PayPal payment redirect.
            # Could be stored on Order but that would mean adding artist_id to all orders.
            # PayPal has no mechanism to return parameters.
            request.session['artist_id'] = self.artist_id

        flow_type = request.POST.get('flow_type')
        if flow_type:
            # Set flow_type in session b/c there's no easy way
            # of passing it through the order.
            request.session['flow_type'] = flow_type

        submission = self.build_submission()
        submission['payment_kwargs']['payment_method'] = payment_method

        return self.submit(**submission)

    def submit(self, user, basket,
               shipping_address, shipping_method,
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

        first_name, last_name = self.checkout_session.get_reservation_name()

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
            self.handle_payment(order_number, order_total, basket_lines,
                                shipping_charge=str(shipping_charge.incl_tax), **payment_kwargs)
        except RedirectRequired as e:
            # Redirect required (eg PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            return http.HttpResponseRedirect(e.url)
        except RedirectRequiredAjax as e:
            # Redirect required (eg PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            print('****************************')
            print('JsonResponse: Basket: ', self.request.basket, ' ', self.request.basket.pk)
            print('Basket: ', basket, ' ', basket.pk)
            print('Submitted basket: ', self.checkout_session.get_submitted_basket_id())
            return http.JsonResponse({'payment_url': e.url})
        except UnableToTakePayment as e:
            print('Exception ===>')
            import sys, traceback
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            print(str(e))
            # Something went wrong with payment but in an anticipated way.  Eg
            # their bankcard has expired, wrong card number - that kind of
            # thing. This type of exception is supposed to set a friendly error
            # message that makes sense to the customer.
            msg = six.text_type(e) + "."
            error_msg = error_msg.format(msg)
            print('******************')
            print('UnableToTakePayment: ')
            print(error_msg)
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
            print(str(e))
            msg = six.text_type(e) + "."
            logger.error("Order #%s: payment error (%s)", order_number, msg,
                         exc_info=True)
            self.restore_frozen_basket()
            error_msg = error_msg.format(msg)
            print('******************')
            print('PaymentError: ')
            print(error_msg)

            if self.request.is_ajax():
                return http.JsonResponse({'error': error_msg})
            else:
                return self.render_payment_details(
                    self.request, error=error_msg, **payment_kwargs)
        except Exception as e:
            # Unhandled exception - hopefully, you will only ever see this in
            # development...
            print('Exception ===>')
            import sys, traceback
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            print(str(e))

            logger.error(
                "Order #%s: unhandled exception while taking payment (%s)",
                order_number, e, exc_info=True)
            self.restore_frozen_basket()
            error_msg = str(e).format("")
            print('******************')
            print(error_msg)

            if self.request.is_ajax():
                return http.JsonResponse({'error': error_msg})
            else:
                return self.render_preview(
                    self.request, error=error_msg, **payment_kwargs)

        signals.post_payment.send_robust(sender=self, view=self)

        # If all is ok with payment, try and place order
        logger.info("Order #%s: payment successful, placing order",
                    order_number)

        try:
            order_kwargs.update({'order_type': basket.get_order_type()})
            response = self.handle_order_placement(
                order_number, user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, **order_kwargs)

            return response
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

        return items

    def handle_payment(self, order_number, total, basket_lines, shipping_charge=0.00, **kwargs):

        basket_line = basket_lines.first()
        basket = basket_line.basket
        self.card_token = self.request.POST.get('card_token')
        self.event = basket.get_tickets_event()
        payment_method = kwargs.get('payment_method')

        currency = total.currency
        if self.card_token:
            self.total = total
            self.total_deductable = basket._get_deductable_physical_total()
            self.payment_id = self.handle_stripe_payment(order_number, basket_lines, **kwargs)
            source_name = 'Stripe Credit Card'
            source_type, __ = SourceType.objects.get_or_create(name=source_name)
            source = Source(
                source_type=source_type,
                currency=currency,
                amount_allocated=total.incl_tax,
                amount_debited=total.incl_tax,
                reference=self.payment_id)
            self.add_payment_source(source)
            self.add_payment_event('Purchase', total.incl_tax, reference=self.payment_id)


        elif payment_method == 'paypal':
            item_list = [] # self.get_item_list(basket_lines)
            self.amount = str(total.incl_tax)
            # 'handle_paypal_payment' returns a RedirectRequiredException
            # and the flow will be completed in ExecutePaypalPayment
            self.handle_paypal_payment(
                currency, item_list,
                shipping_charge=shipping_charge)

    def payment_description(self, order_number, total, **kwargs):
        return 'Order #{0} at SmallsLIVE'.format(order_number)

    def payment_metadata(self, order_number, total, basket_lines, **kwargs):
        items = {}
        for idx, item in enumerate(basket_lines, start=1):
            item_key = u'item{0}'.format(idx)
            items[item_key] = u'{0}, qty: {1}'.format(item.product.get_title(), item.quantity)
        items['order_number'] = order_number

        return items

    def handle_successful_order(self, order):
        self.order = order

        return self.handle()


class ExecutePayPalPaymentView(AssignProductMixin,
                               OrderPlacementMixin,
                               PayPalMixin,
                               SuccessfulOrderMixin,
                               View):
    """
    """

    def __init__(self, *args, **kwargs):
        super(ExecutePayPalPaymentView, self).__init__(*args, **kwargs)
        self.order = None
        self.payment_id = None
        self.tickets_type = None
        self.product_id = None
        self.event_id = None
        self.artist_id = None
        self.card_token = None

    def get(self, request, *args, **kwargs):

        """
        Receive callback from PayPal after the user has authorized the payment there.
        GET /store/checkout/paypal/execute/?paymentId=PAY-1LV98277E5422594XLP4E2MY&token=EC-1FB41424NL964725H&PayerID=EXH9W7JL6NSN8
        Confirm the payment and place the order
        """

        # Get flow type from session
        flow_type = self.request.session.get('flow_type')
        self.product_id = self.request.session.get('product_id') or None
        self.event_id = self.request.session.get('event_id') or None
        self.event_slug = self.request.session.get('event_slug') or None
        self.artist_id = self.request.session.get('artist_id') or None

        try:
            self.handle_payment()
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

        if self.product_id:
            del self.request.session['product_id']

        if self.event_id:
            del self.request.session['event_id']
            del self.request.session['event_slug']

        if self.artist_id:
            del self.request.session['artist_id']

        if flow_type:
            del self.request.session['flow_type']
            sl_utils.clean_messages(self.request)

            redirect_url = reverse(
                'become_supporter_complete') + '?payment_id={}&flow_type={}'.format(
                self.payment_id, flow_type)

            if self.product_id:
                redirect_url += '&product_id={}'.format(self.product_id)
            if self.event_id:
                redirect_url += '&event_id={}&event_slug={}'.format(
                    self.event_id, self.event_slug)
            if self.artist_id:
                redirect_url += '&artist_id={}'.format(
                    self.artist_id)

            return http.HttpResponseRedirect(redirect_url)
        else:
            return http.HttpResponseRedirect(reverse(
                'checkout:thank-you') + '?payment_id={}'.format(self.payment_id))

    def handle_payment(self):

        # request.basket doesn't work b/c the basket is frozen
        basket = self.get_submitted_basket()
        self.event = basket.get_tickets_event()
        self.payment_id = self.execute_payment()

        # TODO: check that the strategy is correct for Tracks (right stock record).
        # If basket has tracks, it's probably to use custom strategy.
        strategy = selector.strategy(request=self.request, user=self.request.user)
        basket.strategy = strategy

        order_number = self.checkout_session.get_order_number()
        user = self.request.user
        shipping_address = self.get_shipping_address(basket)
        shipping_method = Repository().get_default_shipping_method(
            basket=basket, user=user,
            request=self.request)
        shipping_charge = shipping_method.calculate(basket)
        billing_address = self.get_billing_address(shipping_address)
        order_total = self.get_order_totals(
            basket, shipping_charge=shipping_charge)

        total_incl_tax = basket.total_incl_tax

        # Record payment source
        order_kwargs = {'order_type': basket.get_order_type()}
        if self.event:
            venue = self.event.venue
            self.tickets_type = venue.name.lower()
            order_kwargs['status'] = 'Completed'
            payment_source = '{} PayPal'.format(venue.name)
            payment_event = 'Sold'
        else:
            payment_source = 'PayPal'
            payment_event = 'Purchase'

        source_type, is_created = SourceType.objects.get_or_create(
            name=payment_source)
        source = Source(source_type=source_type,
                        currency='USD',
                        amount_allocated=total_incl_tax,
                        amount_debited=total_incl_tax,
                        reference=self.payment_id)
        self.add_payment_source(source)
        self.add_payment_event(
            payment_event, total_incl_tax, reference=self.payment_id)

        user = self.request.user
        first_name, last_name = self.checkout_session.get_reservation_name()

        if user.is_anonymous():
            user = None
            guest_email = self.checkout_session.get_guest_email()
            order_kwargs['guest_email'] = guest_email
        if first_name and last_name:
            order_kwargs.update({
                'first_name': first_name,
                'last_name': last_name
            })

        try:
            self.handle_order_placement(order_number, user, basket,
                                        shipping_address, shipping_method,
                                        shipping_charge, billing_address, order_total,
                                        **order_kwargs)
        except ValueError as e:
            # Probably order is already  placed because of a reload
            logging.error(str(e))
            print(e)
            pass

    def handle_successful_order(self, order):
        self.order = order
        return self.handle()

# =========
# Thank you
# =========

class ThankYouView(generic.DetailView):
    """
    Displays the 'thank you' page which summarises the order just submitted.
    """
    template_name = 'checkout/thank_you.html'
    context_object_name = 'order'

    def get_object(self):
        # We allow superusers to force an order thank-you page for testing
        order = None
        if self.request.user.is_superuser:
            if 'order_number' in self.request.GET:
                order = Order._default_manager.get(
                    number=self.request.GET['order_number'])
            elif 'order_id' in self.request.GET:
                order = Order._default_manager.get(
                    id=self.request.GET['order_id'])

        if not order:
            if 'checkout_order_id' in self.request.session:
                order = Order._default_manager.get(
                    pk=self.request.session['checkout_order_id'])
            else:
                raise http.Http404(_("No order found"))

        return order

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        # Remember whether this view has been loaded.
        # Only send tracking information on the first load.
        key = 'order_{}_thankyou_viewed'.format(ctx['order'].pk)
        if not self.request.session.get(key, False):
            self.request.session[key] = True
            ctx['send_analytics_event'] = True
        else:
            ctx['send_analytics_event'] = False

        return ctx
